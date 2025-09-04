import joblib, json, numpy as np, shap
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "models"
GB_PATH = BASE / "gb_pipeline.joblib"
LR_PATH = BASE / "lr_pipeline.joblib"
META_PATH = BASE / "metadata.json"
LR_BG_TRANS_PATH = BASE / "lr_bg_trans.npy"

gb_model = joblib.load(GB_PATH)  # Pipeline
lr_model = joblib.load(LR_PATH)  # Pipeline

meta = json.load(open(META_PATH))
FEATURES = meta["features"]
LOW_T = float(meta["risk_bands"]["low"])
HIGH_T = float(meta["risk_bands"]["high"])

# Background for LinearExplainer
bg_trans = np.load(LR_BG_TRANS_PATH) if LR_BG_TRANS_PATH.exists() else None
if bg_trans is None:
    # fallback tiny zero background with correct transformed shape:
    # try to infer transformed size by passing one synthetic row
    import pandas as pd
    fake = pd.DataFrame([ [0]*len(FEATURES) ], columns=FEATURES)
    trans = lr_model.named_steps["preprocess"].transform(fake)
    bg_trans = np.zeros((50, trans.shape[1]))

# SHAP explainer for LR
try:
    explainer = shap.LinearExplainer(lr_model.named_steps["lr"], bg_trans)
except Exception:
    # fallback: KernelExplainer (slower; consider caching)
    explainer = shap.KernelExplainer(lr_model.named_steps["lr"].predict_proba, bg_trans)
