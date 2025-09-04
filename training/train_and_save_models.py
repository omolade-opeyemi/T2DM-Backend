import json, joblib, numpy as np, pandas as pd
from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression

# ---- Load data
csv_path = Path("Diabetes_Final_Data_V2.csv")
df = pd.read_csv(csv_path)

# Ensure target is numeric 0/1
if df["diabetic"].dtype == object:
    df["diabetic"] = (
        df["diabetic"].astype(str).str.strip().str.lower()
        .map({"yes":1,"y":1,"positive":1,"no":0,"n":0,"negative":0})
    )
df["diabetic"] = df["diabetic"].fillna(df["diabetic"].mode(dropna=True)[0]).astype(int)

if "cardiovascular_disease" in df.columns and "cvd" not in df.columns:
    df["cvd"] = df["cardiovascular_disease"]
FEATURES = [
    "age","gender","pulse_rate","systolic_bp","diastolic_bp","glucose",
    "height","weight","bmi","family_diabetes","hypertensive",
    "family_hypertension","cvd","stroke"
]
X = df[FEATURES].copy()
y = df["diabetic"].values

# split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.30, stratify=y, random_state=42
)

# preprocess
num_cols = [c for c in FEATURES if pd.api.types.is_numeric_dtype(X[c])]
cat_cols = [c for c in FEATURES if c not in num_cols]

numeric_pre = Pipeline([("imputer", SimpleImputer(strategy="mean")),
                        ("scaler", StandardScaler())])
categorical_pre = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                            ("enc", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))])

preprocess = ColumnTransformer([("num", numeric_pre, num_cols),
                                ("cat", categorical_pre, cat_cols)],
                               remainder="drop")

# models
gb = Pipeline([("preprocess", preprocess),
               ("gb", GradientBoostingClassifier(
                    n_estimators=300, learning_rate=0.05, max_depth=3,
                    subsample=0.8, random_state=42))])

lr = Pipeline([("preprocess", preprocess),
               ("lr", LogisticRegression(
                    max_iter=1000, solver="liblinear", class_weight="balanced",
                    random_state=42))])

gb.fit(X_train, y_train)
lr.fit(X_train, y_train)

# Save artifacts
Path("models").mkdir(exist_ok=True)
joblib.dump(gb, "models/gb_pipeline.joblib")
joblib.dump(lr, "models/lr_pipeline.joblib")

# risk bands & feature list
meta = {
    "features": FEATURES,
    "risk_bands": {"low": 0.20, "high": 0.50}  # tune as needed or set 90% specificity threshold
}
json.dump(meta, open("models/metadata.json","w"))

# For SHAP: save a small transformed background for LinearExplainer
X_bg = X_train.sample(min(200, len(X_train)), random_state=42)  # small background
X_bg_trans = lr.named_steps["preprocess"].transform(X_bg)
np.save("models/lr_bg_trans.npy", X_bg_trans)

print("Saved: models/gb_pipeline.joblib, models/lr_pipeline.joblib, models/metadata.json, models/lr_bg_trans.npy")
