import json
import os
import sqlite3
from typing import Any, Dict, List

import numpy as np
from PIL import Image, ImageOps
import tensorflow as tf

from src.config import (
    CLASS_INDICES_PATH,
    DB_PATH,
    MODEL_PATH,
    OOD_CLASS_KEY,
)

CONFIDENCE_THRESHOLD = 0.62
MARGIN_THRESHOLD = 0.15

def load_class_map() -> Dict[int, str]:
    with open(CLASS_INDICES_PATH, "r", encoding="utf-8") as f:
        mapping = json.load(f)
    return {int(idx): name for name, idx in mapping.items()}


def load_leafcheck_model() -> tf.keras.Model:
    """Load trained v4 model and bypass the training-only leaf_augmentation layer for deterministic inference."""
    raw_model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    if any(layer.name == "leaf_augmentation" for layer in raw_model.layers):
        inp = tf.keras.Input(shape=(224, 224, 3))
        x = inp
        for layer in raw_model.layers[2:]:  # Skip input_layer (0) and leaf_augmentation (1)
            x = layer(x, training=False) if layer.name in ("efficientnetb0", "batch_normalization", "dropout", "dropout_1") else layer(x)
        return tf.keras.Model(inp, x, name="LeafCheck_EfficientNetB0_Inference")
    return raw_model


def get_monograph(class_key: str) -> Dict[str, Any]:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Database not found at {DB_PATH}. Run `python src/build_db.py` first.")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM monographs WHERE class_key = ?", (class_key,))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else {}


def prepare_4view_batch(pil_img: Image.Image, target_size=(224, 224)) -> np.ndarray:
    """EXIF-correct, aspect-preserving center crop, resize to 224x224, and build 4-view TTA batch."""
    img = ImageOps.exif_transpose(pil_img).convert("RGB")
    img = ImageOps.fit(img, target_size, method=Image.Resampling.LANCZOS)
    arr = np.asarray(img, dtype=np.float32)

    v1 = arr
    v2 = np.flip(arr, axis=1)
    v3 = np.rot90(arr, k=1)
    v4 = np.rot90(arr, k=3)
    return np.stack([v1, v2, v3, v4], axis=0)

def predict_leaf(
    pil_img: Image.Image,
    model: tf.keras.Model,
    idx_to_class: Dict[int, str],
    conf_threshold: float = CONFIDENCE_THRESHOLD,
    margin_threshold: float = MARGIN_THRESHOLD,
) -> Dict[str, Any]:
    """Run 4-view TTA inference and dual OOD gate on a PIL image."""
    tta_batch = prepare_4view_batch(pil_img)
    preds = model.predict(tta_batch, verbose=0)
    mean_probs = np.mean(preds, axis=0)

    ranked_indices = np.argsort(mean_probs)[::-1]
    top1_idx = int(ranked_indices[0])
    top2_idx = int(ranked_indices[1])

    top1_key = idx_to_class[top1_idx]
    top1_prob = float(mean_probs[top1_idx])
    top2_prob = float(mean_probs[top2_idx])
    margin = top1_prob - top2_prob

    top3: List[Dict[str, Any]] = []
    for idx in ranked_indices[:3]:
        ckey = idx_to_class[int(idx)]
        prob = float(mean_probs[int(idx)])
        label = (
            "Non-Medicinal / Unknown Foliage"
            if ckey == OOD_CLASS_KEY
            else ckey.split("_", 1)[1].replace("_", " ")
        )
        top3.append({"class_key": ckey, "label": label, "probability": prob})

    is_ood = False
    ood_reason = ""
    if top1_key == OOD_CLASS_KEY:
        is_ood = True
        ood_reason = (
            f"Classified as outside the 10-species Philippine herbal reference roster "
            f"({top1_prob * 100:.1f}% non-target match)."
        )
    elif top1_prob < conf_threshold or margin < margin_threshold:
        is_ood = True
        ood_reason = (
            f"Low botanical confidence ({top1_prob * 100:.1f}%, margin {margin * 100:.1f}%). "
            "Image may show an unsupported plant, blurry focus, or non-leaf background."
        )

    if is_ood:
        return {
            "status": "REJECTED_OOD",
            "class_key": OOD_CLASS_KEY,
            "confidence": top1_prob,
            "margin": margin,
            "ood_reason": ood_reason,
            "top3": top3,
            "monograph": None,
        }

    monograph = get_monograph(top1_key)
    return {
        "status": "IDENTIFIED",
        "class_key": top1_key,
        "confidence": top1_prob,
        "margin": margin,
        "ood_reason": "",
        "top3": top3,
        "monograph": monograph,
    }