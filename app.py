import streamlit as st
from src.predict import load_class_map, load_leafcheck_model
from src.ui_components import render_guide_tab, render_metrics_tab, render_scanner_tab

st.set_page_config(
    page_title="LeafCheck | Herbal Plant Authentication & Safety",
    page_icon="🌿",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.title("🌿 LeafCheck")
st.caption("Philippine Medicinal Plant Authentication & Toxicology Safety System")

st.warning(
    "⚠️ **Medical & Botanical Disclaimer:** Automated visual classification is an educational decision-support tool, "
    "**not** a medical prescription or toxicity guarantee. Always verify plant identity with a qualified botanist "
    "or licensed healthcare professional before internal or topical use."
)

if "leafcheck_model" not in st.session_state:
    with st.spinner("Initializing EfficientNetB0 botanical inference engine..."):
        try:
            st.session_state["leafcheck_model"] = load_leafcheck_model()
            st.session_state["idx_to_class"] = load_class_map()
        except Exception as e:
            st.error(f"Failed to load LeafCheck v4 model artifacts: {e}")
            st.stop()

model = st.session_state["leafcheck_model"]
idx_to_class = st.session_state["idx_to_class"]

tab_scan, tab_guide, tab_metrics = st.tabs([
    "📸 Leaf Scanner",
    "🌱 10-Species Guide",
    "📊 Validation Metrics",
])

with tab_scan:
    render_scanner_tab(model, idx_to_class)

with tab_guide:
    render_guide_tab()

with tab_metrics:
    render_metrics_tab()