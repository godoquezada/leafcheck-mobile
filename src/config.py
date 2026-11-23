from pathlib import Path

IMG_SIZE = (224, 224)

MODEL_PATH = Path("models/leafcheck_model_v4.keras")
CLASS_INDICES_PATH = Path("models/class_indices.json")
DB_PATH = Path("data/herbal_monographs.db")

EVAL_DIR = Path("docs/evaluation")
MODEL_COMPARISON_PATH = EVAL_DIR / "model_comparison.csv"
CONFUSION_MATRIX_PATH = EVAL_DIR / "confusion_matrix_v4.png"
TRAINING_CURVES_PATH = EVAL_DIR / "training_curves_v4.png"
CLASSIFICATION_REPORT_PATH = EVAL_DIR / "classification_report_v4.txt"

OOD_CLASS_KEY = "11_Non_Medicinal_Unknown"

THRESHOLD_MODES = {
    "Balanced Field Mode (62% Conf / 15% Margin — Recommended)": (0.62, 0.15),
    "Outdoor Flexible Mode (50% Conf / 10% Margin — Challenging Lighting)": (0.50, 0.10),
    "Strict Safety Mode (78% Conf / 20% Margin — High-Certainty Gate)": (0.78, 0.20),
}