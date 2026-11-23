import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import numpy as np
import pandas as pd
import requests
import tensorflow as tf
from PIL import Image, ImageOps

# Configuration
IMG_SIZE = (224, 224)
PHOTOS_PER_SPECIES = 10
THRESHOLD = 0.65
TEST_DIR = Path("unseen_field_test")
TEST_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "LeafCheck-Benchmark-Evaluator/1.0"}

# Fix the 2 dataset folder scientific name typos for accurate iNaturalist taxonomy lookup
SCI_NAME_FIXES = {
    "Averrhoea bilimbi": "Averrhoa bilimbi",
    "Pepromia pellucida": "Peperomia pellucida",
}

def download_image(url: str, save_path: Path) -> bool:
    if save_path.exists():
        return True
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(r.content)
            with Image.open(save_path) as im:
                im.verify()
            return True
    except Exception:
        if save_path.exists():
            save_path.unlink()
    return False

def fetch_unseen_photos(class_key: str, sci_name: str, count: int = 10) -> list[Path]:
    species_dir = TEST_DIR / class_key
    species_dir.mkdir(parents=True, exist_ok=True)

    existing = sorted(species_dir.glob("*.jpg"))
    if len(existing) >= count:
        return existing[:count]

    query_taxon = SCI_NAME_FIXES.get(sci_name, sci_name)
    # Sort by newest observations ("created_at") to avoid overlap with training ("votes")
    params = {
        "taxon_name": query_taxon,
        "quality_grade": "research",
        "photos": "true",
        "per_page": 30,
        "order_by": "created_at",
        "order": "desc",
    }
    try:
        resp = requests.get(
            "https://api.inaturalist.org/v1/observations",
            params=params,
            headers=HEADERS,
            timeout=15,
        ).json()
        urls = []
        for obs in resp.get("results", []):
            for photo in obs.get("photos", []):
                u = photo.get("url", "").replace("square", "medium")
                if u.startswith("http"):
                    urls.append(u)
                    break
            if len(urls) >= count:
                break

        with ThreadPoolExecutor(max_workers=6) as ex:
            futures = [
                ex.submit(download_image, u, species_dir / f"unseen_{i+1:02d}.jpg")
                for i, u in enumerate(urls)
            ]
            for f in futures:
                f.result()
    except Exception as e:
        print(f"  [Warning] Failed fetching {class_key}: {e}")

    return sorted(species_dir.glob("*.jpg"))[:count]

def predict_with_tta(model, pil_img: Image.Image) -> np.ndarray:
    """Exact 4-view Test-Time Augmentation used in app.py."""
    w, h = pil_img.size
    crop_box = (int(w * 0.08), int(h * 0.08), int(w * 0.92), int(h * 0.92))
    center_crop = pil_img.crop(crop_box)

    views = [
        pil_img.resize(IMG_SIZE),
        ImageOps.mirror(pil_img).resize(IMG_SIZE),
        center_crop.resize(IMG_SIZE),
        ImageOps.mirror(center_crop).resize(IMG_SIZE),
    ]
    batch = np.stack([np.array(v, dtype=np.float32) for v in views], axis=0)
    preds = model.predict(batch, verbose=0)
    return np.mean(preds, axis=0)

def main():
    print("1/3 Loading EfficientNetB0 model, class indices, and species list...")
    model = tf.keras.models.load_model("models/leafcheck_mobilenetv2.keras")
    with open("models/class_indices.json", "r", encoding="utf-8") as f:
        class_indices = json.load(f)

    summary_path = Path("data/data_summary.csv") if Path("data/data_summary.csv").exists() else Path("data_summary.csv")
    df = pd.read_csv(summary_path)
    herbs_df = df[df["class_key"] != "Non_Medicinal_Unknown"].copy()

    print(f"2/3 Downloading {PHOTOS_PER_SPECIES} unseen iNaturalist field photos per herb into '{TEST_DIR}/'...")
    species_files = {}
    for idx, row in herbs_df.iterrows():
        ck = row["class_key"]
        sci = row["scientific_name"]
        files = fetch_unseen_photos(ck, sci, PHOTOS_PER_SPECIES)
        species_files[ck] = (sci, files)
        print(f"  [{len(species_files):02d}/40] {ck}: {len(files)}/{PHOTOS_PER_SPECIES} photos ready")
        time.sleep(0.25)

    print("\n3/3 Running 4-view TTA evaluation across all downloaded field photos...")
    report_rows = []
    all_detailed_rows = []

    for ck, (sci, files) in species_files.items():
        if not files:
            continue
        raw_hits = 0
        accepted_hits = 0
        rejected_count = 0
        confidences = []
        wrong_preds = []

        for img_path in files:
            with Image.open(img_path) as im:
                rgb = im.convert("RGB")
            preds = predict_with_tta(model, rgb)
            top_idx = int(np.argmax(preds))
            top_conf = float(preds[top_idx])
            pred_key = class_indices[str(top_idx)]

            is_raw_correct = (pred_key == ck)
            is_accepted_correct = is_raw_correct and (top_conf >= THRESHOLD)

            if is_raw_correct:
                raw_hits += 1
            else:
                wrong_preds.append(f"{pred_key} ({top_conf:.0%})")

            if top_conf < THRESHOLD or pred_key == "Non_Medicinal_Unknown":
                rejected_count += 1
            if is_accepted_correct:
                accepted_hits += 1

            confidences.append(top_conf)
            all_detailed_rows.append({
                "true_species": ck,
                "image": img_path.name,
                "predicted_species": pred_key,
                "confidence": round(top_conf, 4),
                "raw_correct": is_raw_correct,
                "passed_65_threshold": is_accepted_correct,
            })

        n = len(files)
        report_rows.append({
            "class_key": ck,
            "scientific_name": sci,
            "tested": n,
            "raw_top1_acc_%": round((raw_hits / n) * 100, 1),
            "accepted_at_65_%": round((accepted_hits / n) * 100, 1),
            "rejected_count": rejected_count,
            "avg_confidence_%": round(float(np.mean(confidences)) * 100, 1),
            "common_confusions": "; ".join(wrong_preds[:3]) if wrong_preds else "None",
        })

    report_df = pd.DataFrame(report_rows).sort_values(by=["raw_top1_acc_%", "avg_confidence_%"], ascending=[True, True])
    detail_df = pd.DataFrame(all_detailed_rows)

    report_df.to_csv("species_benchmark_report.csv", index=False)
    detail_df.to_csv("species_benchmark_detailed.csv", index=False)

    print("\n================ BENCHMARK SUMMARY ================")
    print(f"Total Unseen Field Images Evaluated: {len(detail_df)}")
    print(f"Overall Raw Top-1 Accuracy:          {detail_df['raw_correct'].mean():.2%}")
    print(f"Overall Accepted Accuracy (>=65%):   {detail_df['passed_65_threshold'].mean():.2%}")
    print("\nLowest-Scoring Species (Candidates for Extra Training):")
    print(report_df.head(10)[["class_key", "raw_top1_acc_%", "accepted_at_65_%", "avg_confidence_%", "common_confusions"]].to_string(index=False))
    print("\nSaved full results to 'species_benchmark_report.csv' and all images to 'unseen_field_test/'.")

if __name__ == "__main__":
    main()