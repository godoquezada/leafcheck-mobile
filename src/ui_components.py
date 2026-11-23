import os
import sqlite3
import pandas as pd
import streamlit as st
from PIL import Image, UnidentifiedImageError

from src.config import (
    CLASSIFICATION_REPORT_PATH,
    CONFUSION_MATRIX_PATH,
    DB_PATH,
    MODEL_COMPARISON_PATH,
    OOD_CLASS_KEY,
    THRESHOLD_MODES,
    TRAINING_CURVES_PATH,
)
from src.predict import predict_leaf


@st.cache_data
def load_all_monographs() -> list[dict]:
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM monographs ORDER BY class_key ASC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def render_scanner_tab(model, idx_to_class: dict):
    with st.expander("⚙️ Validation & Camera Settings", expanded=False):
        mode_label = st.radio(
            "Out-of-Distribution (OOD) Safety Gate",
            options=list(THRESHOLD_MODES.keys()),
            index=0,
        )
        conf_threshold, margin_threshold = THRESHOLD_MODES[mode_label]

        st.markdown(
            "**Field Capture Best Practices:**\n"
            "- Fill **70–80% of the frame** with 1–3 clear leaflets (avoid distant whole-tree shots).\n"
            "- On mobile, **Take / Upload Photo** opens your phone's native autofocus camera."
        )

    input_method = st.radio(
        "Capture Method:",
        ["📱 Take / Upload Photo (Recommended on Phone)", "📷 Live Browser Camera"],
        horizontal=True,
    )

    if "Live Browser" in input_method:
        uploaded_file = st.camera_input("Point rear camera at a leaf or sprig and capture")
    else:
        uploaded_file = st.file_uploader(
            "Tap below to open phone camera or choose from gallery",
            type=["jpg", "jpeg", "png", "webp"],
        )

    if uploaded_file is None:
        return

    try:
        pil_img = Image.open(uploaded_file)
        pil_img.load()
    except (UnidentifiedImageError, OSError, ValueError) as err:
        st.error(f"Invalid or corrupted image file: {err}")
        return

    st.image(pil_img, caption="Submitted Leaf Image", width=340)

    with st.spinner("Analyzing leaf venation and morphology (4-View TTA)..."):
        result = predict_leaf(
            pil_img=pil_img,
            model=model,
            idx_to_class=idx_to_class,
            conf_threshold=conf_threshold,
            margin_threshold=margin_threshold,
        )

    _render_prediction_result(result)


def _render_prediction_result(result: dict):
    st.divider()
    st.subheader("Classification Result")

    top3 = result.get("top3", [])

    if result["status"] == "REJECTED_OOD":
        st.error(
            f"🚫 **Out-of-Scope / Unrecognized Specimen**\n\n"
            f"{result['ood_reason']}\n\n"
            "This specimen was rejected to prevent false medicinal identification. "
            "Ensure the leaf belongs to one of the 10 supported Philippine species and is photographed clearly up close."
        )
        with st.expander("View Top-3 Raw Model Probabilities", expanded=True):
            for item in top3:
                st.write(f"- **{item['label']}**: `{item['probability']:.2%}`")
        return

    mono = result.get("monograph") or {}
    safety_tier = mono.get("safety_tier", "")
    common_name = mono.get("common_name", result["class_key"])
    sci_name = mono.get("scientific_name", "N/A")

    # Tiered Safety Alert Header
    if safety_tier == "CRITICAL_POISON":
        st.error(f"☠️ **{mono.get('safety_banner', 'CRITICAL POISON WARNING')}**\n\n**Matched Plant:** {common_name} (*{sci_name}*)")
    elif safety_tier == "TOXIC_ALERT":
        st.error(f"⚠️ **{mono.get('safety_banner', 'TOXIC INGESTION ALERT')}**\n\n**Matched Plant:** {common_name} (*{sci_name}*)")
    else:
        st.success(f"✅ **Matched Species:** {common_name} (*{sci_name}*)")
        if mono.get("safety_banner"):
            st.info(f"🛡️ **{mono['safety_banner']}**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Confidence (4-View TTA)", f"{result['confidence']:.1%}")
    col2.metric("Top-2 Margin", f"+{result['margin']:.1%}")
    col3.metric("Botanical Family", mono.get("family", "N/A"))

    st.markdown(f"**Local Philippine Names:** {mono.get('local_names', 'N/A')}")
    st.markdown(f"**Key Botanical Markers:** {mono.get('botanical_markers', 'N/A')}")
    st.markdown(f"**Ethnobotanical / Clinical Context:** {mono.get('traditional_uses', 'N/A')}")

    if safety_tier in ("CRITICAL_POISON", "TOXIC_ALERT"):
        st.warning(f"**Handling & Hazard Warning:** {mono.get('preparation', '')}")
        st.error(f"**Toxicology & Contraindications:** {mono.get('contraindications', '')}")
    else:
        st.markdown(f"**Traditional Preparation:** {mono.get('preparation', 'N/A')}")
        st.warning(f"**Contraindications & Precautions:** {mono.get('contraindications', 'N/A')}")

    st.caption(f"Reference: {mono.get('reference', 'DOH / PITAHC Philippine Herbal Pharmacopoeia')}")

    with st.expander("View Top-3 Candidate Predictions"):
        for item in top3:
            st.write(f"- **{item['label']}**: `{item['probability']:.2%}`")


def render_guide_tab():
    st.subheader("Supported Philippine Roster (8 Medicinal Herbs + 2 Toxic Look-Alikes)")
    st.caption("Search by local name (e.g., Lagundi, Ampalaya, Tsaang Gubat, Adelfa) or scientific name.")

    monographs = load_all_monographs()
    if not monographs:
        st.warning("Monograph database not found. Run `python src/build_db.py` first.")
        return

    search_q = st.text_input("🔍 Filter species list", placeholder="Type a local or scientific name...")

    rows = []
    for m in monographs:
        tier = m["safety_tier"]
        if tier == "CRITICAL_POISON":
            badge = "☠️ LETHAL POISON"
        elif tier == "TOXIC_ALERT":
            badge = "⚠️ TOXIC HAZARD"
        elif tier == "SAFE_DOH_APPROVED":
            badge = "✅ DOH Approved"
        else:
            badge = "🌿 Traditional / Culinary"

        rows.append({
            "Common Name": m["common_name"],
            "Scientific Name": m["scientific_name"],
            "Local Names": m["local_names"],
            "Safety Classification": badge,
        })

    guide_df = pd.DataFrame(rows)
    if search_q.strip():
        mask = (
            guide_df["Common Name"].str.contains(search_q, case=False, na=False)
            | guide_df["Scientific Name"].str.contains(search_q, case=False, na=False)
            | guide_df["Local Names"].str.contains(search_q, case=False, na=False)
        )
        guide_df = guide_df[mask]

    st.dataframe(guide_df, use_container_width=True, hide_index=True)

    st.markdown("### Detailed Botanical & Safety Monographs")
    for m in monographs:
        if search_q.strip():
            blob = f"{m['common_name']} {m['scientific_name']} {m['local_names']}".lower()
            if search_q.strip().lower() not in blob:
                continue
        icon = "☠️" if m["safety_tier"] == "CRITICAL_POISON" else ("⚠️" if m["safety_tier"] == "TOXIC_ALERT" else "🌿")
        with st.expander(f"{icon} {m['common_name']} — {m['scientific_name']}"):
            st.markdown(f"**Local Names:** {m['local_names']} | **Family:** {m['family']}")
            st.markdown(f"**Botanical Markers:** {m['botanical_markers']}")
            st.markdown(f"**Uses / Status:** {m['traditional_uses']}")
            st.markdown(f"**Preparation / Action:** {m['preparation']}")
            st.markdown(f"**Contraindications:** {m['contraindications']}")


def render_metrics_tab():
    st.subheader("Model Architecture & Comparative Benchmark (LeafCheck v4)")
    st.caption(
        "Evaluated on 1,650 unseen Research-Grade original iNaturalist test images "
        "(150 per class across 10 Philippine species + 1 Out-of-Distribution rejection class)."
    )

    if MODEL_COMPARISON_PATH.exists():
        comp_df = pd.read_csv(MODEL_COMPARISON_PATH)
        st.dataframe(comp_df, use_container_width=True, hide_index=True)
    else:
        st.info("Place `model_comparison.csv` inside `docs/evaluation/` to view the benchmark table.")

    if CONFUSION_MATRIX_PATH.exists():
        st.subheader("Confusion Matrix (1,650 Unseen Test Images)")
        st.image(str(CONFUSION_MATRIX_PATH), use_container_width=True)

    if TRAINING_CURVES_PATH.exists():
        st.subheader("Two-Stage Transfer Learning Curves")
        st.image(str(TRAINING_CURVES_PATH), use_container_width=True)

    if CLASSIFICATION_REPORT_PATH.exists():
        with st.expander("View Full Per-Class Classification Report"):
            st.code(CLASSIFICATION_REPORT_PATH.read_text(encoding="utf-8"), language="text")