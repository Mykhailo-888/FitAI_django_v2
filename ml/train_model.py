import numpy as np
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path
from sklearn.model_selection import train_test_split

from ml.fit_model_core import FitnessNeuralNet

print("=== Training Fitness Model (PHYSICS-BASED TARGETS) ===")

# ================= LOAD DATA =================
dataset_path = r"C:\FitAI_django\data\edited_23_params_realistic.csv"
df = pd.read_csv(dataset_path)

print(f"Using dataset: {os.path.basename(dataset_path)} | Shape: {df.shape}")

X = df.values.astype(np.float64)

# ================= BUILD PHYSICS TARGETS =================
age = df["Age"].values
weight = df["Weight_kg"].values
height = df["Height_cm"].values
hrv = df["HRV"].values
sleep = df["Sleep_hours"].values
stress = df["Emotional_stress"].values
crp = df["CRP_mg_l"].values
rhr = df["Resting_heart_rate_bpm"].values
testo = df["Testosterone_ng_dl"].values
alcohol = df["Alcohol_units_per_week"].values

# ---- 1. Calories burned
calories = (
    10 * weight + 5 * height - 3 * age +
    200 * sleep - 150 * stress - 50 * crp +
    np.random.normal(0, 200, size=len(df))
)

# ---- 2. 1 km run time
run_1km = (
    8 + 0.03 * rhr - 0.02 * hrv +
    0.2 * stress + 0.1 * crp - 0.3 * sleep +
    np.random.normal(0, 0.3, size=len(df))
)

# ---- 3. Cooper distance
cooper = (
    2.5 + 0.01 * hrv - 0.02 * rhr -
    0.05 * stress - 0.05 * crp + 0.03 * sleep +
    np.random.normal(0, 0.1, size=len(df))
)

# ---- 4. Pull-ups
pullups = (
    10 + 0.05 * testo - 0.03 * weight -
    0.5 * stress - 0.5 * crp +
    np.random.normal(0, 2, size=len(df))
)

# ---- 5. Burpees/hour
burpees = (
    50 + 0.2 * hrv - 0.1 * rhr -
    1.5 * stress - 1.0 * crp + 2 * sleep +
    np.random.normal(0, 10, size=len(df))
)

# ---- 6. 10 km run
run_10km = (
    50 + 0.2 * rhr - 0.1 * hrv +
    2 * stress + 1.5 * crp - 1.0 * sleep +
    np.random.normal(0, 3, size=len(df))
)

# ---- 7. Waist change — сильно більше мінусів
waist = (
    -1.8 * sleep +
    -1.0 * hrv +
    0.6 * stress +
    0.5 * alcohol +
    0.7 * crp +
    0.2 * (weight - 80) +
    -2.0 +                     # сильне зміщення вниз
    np.random.normal(0, 0.8, size=len(df))
)

# ---- 8. Testosterone future
testosterone_future = (
    testo +
    20 * sleep - 30 * stress -
    10 * alcohol - 15 * crp +
    np.random.normal(0, 30, size=len(df))
)

# ================= STACK & CLIP =================
y = np.vstack([calories, run_1km, cooper, pullups, burpees,
               run_10km, waist, testosterone_future]).T

y[:, 0] = np.clip(y[:, 0], 1500, 5000)
y[:, 1] = np.clip(y[:, 1], 3, 12)
y[:, 2] = np.clip(y[:, 2], 1.6, 4.2)   # Cooper test в км (реалістичний діапазон)
y[:, 3] = np.clip(y[:, 3], 0, 40)
y[:, 4] = np.clip(y[:, 4], 20, 300)
y[:, 5] = np.clip(y[:, 5], 30, 120)
y[:, 6] = np.clip(y[:, 6], -6, 4)      # Waist: більше мінусів
y[:, 7] = np.clip(y[:, 7], 200, 1000)

print("Generated targets shape:", y.shape)

# ================= SPLIT =================
X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"Train: {len(X_train)} | Val: {len(X_val)}")

# ================= TRAIN =================
model = FitnessNeuralNet(
    lr=0.0005,
    n_iters=20000,
    embedding_size=48,
    hidden_size=32,
    output_size=8
)

print("Training started...")
model.fit(X_train, y_train, X_val, y_val)

# ================= SAVE MODEL =================
model_path = Path(r"C:\FitAI_django\ml\models\trained_fitness_model_simple.pkl")
model.save_model(str(model_path))
print(f"✅ Model successfully saved: {model_path}")

# ================= SAVE TRAINING HISTORY =================
history = {
    "dataset": os.path.basename(dataset_path),
    "train_samples": int(len(X_train)),
    "val_samples": int(len(X_val)),
    "n_iters": 20000,
    "lr": 0.0005,
    "embedding_size": 48,
    "hidden_size": 32,
    "best_val_loss": float(getattr(model, 'best_val_loss', 0.0)),
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "notes": "physics-based targets with improved waist logic (more negative waist)"
}

history_path = Path(r"C:\FitAI_django\ml\training_history.json")
history_path.parent.mkdir(parents=True, exist_ok=True)

with open(history_path, "w", encoding="utf-8") as f:
    json.dump(history, f, indent=4, ensure_ascii=False)

print(f"✅ Training history saved: {history_path}")
# ================= EXPLAINABILITY (Feature Impact PER OUTPUT) =================
print("\n=== Calculating Feature Impact (PER OUTPUT) ===")

np.random.seed(42)
n_samples = min(50, len(X_train))
sample_idx = np.random.choice(len(X_train), size=n_samples, replace=False)
samples = X_train[sample_idx]

base_preds = model.predict(samples)
feature_names = df.columns.tolist()

# Назви виходів (для зрозумілого виводу)
output_names = [
    "Calories", "1km_Run", "Cooper", "Pull_Ups", "Burpees",
    "10km_Run", "Waist_Change", "Testosterone"
]

# 1. Relative Change (+30%)
print("\n--- Relative Change (+30%) per output ---")
impacts_rel = np.zeros((len(feature_names), len(output_names)))

for i in range(len(feature_names)):
    modified = samples.copy()
    modified[:, i] *= 1.30
    new_preds = model.predict(modified)
    rel_change = np.abs(new_preds - base_preds) / (np.abs(base_preds) + 1e-6)
    impacts_rel[i] = np.mean(rel_change, axis=0)

# Нормалізація по кожному виходу
for j in range(len(output_names)):
    if impacts_rel[:, j].sum() > 0:
        impacts_rel[:, j] = impacts_rel[:, j] / impacts_rel[:, j].sum() * 100

# 2. Gradient-based
print("\n--- Gradient-based (∂y/∂x) per output ---")
eps = 0.05
impacts_grad = np.zeros((len(feature_names), len(output_names)))

for i in range(len(feature_names)):
    modified = samples.copy()
    modified[:, i] += eps
    new_preds = model.predict(modified)
    grad = (new_preds - base_preds) / eps
    impacts_grad[i] = np.mean(np.abs(grad), axis=0)

for j in range(len(output_names)):
    if impacts_grad[:, j].sum() > 0:
        impacts_grad[:, j] = impacts_grad[:, j] / impacts_grad[:, j].sum() * 100

# ================= PRINT TOP FEATURES PER OUTPUT =================
all_results = {}
for j, out_name in enumerate(output_names):
    print(f"\n🔥 Top features for **{out_name}**:")

    # Relative
    sorted_idx = np.argsort(impacts_rel[:, j])[::-1]
    print("  Relative (+30%):")
    for idx in sorted_idx[:6]:
        print(f"    {feature_names[idx]:30s} → {impacts_rel[idx, j]:6.2f}%")

    # Gradient
    print("  Gradient-based:")
    sorted_idx_grad = np.argsort(impacts_grad[:, j])[::-1]
    for idx in sorted_idx_grad[:6]:
        print(f"    {feature_names[idx]:30s} → {impacts_grad[idx, j]:6.2f}%")

    all_results[out_name] = {
        "features": [feature_names[i] for i in sorted_idx[:8]],
        "relative_percent": [float(impacts_rel[i, j]) for i in sorted_idx[:8]],
        "gradient_percent": [float(impacts_grad[i, j]) for i in sorted_idx[:8]]
    }

# ================= SAVE =================
explain_data = {
    "per_output": all_results,
    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

explain_path = Path(r"C:\FitAI_django\ml\feature_importance.json")
with open(explain_path, "w", encoding="utf-8") as f:
    json.dump(explain_data, f, indent=4)

print(f"✅ Feature importance saved: {explain_path}")
print("=== TRAINING COMPLETED SUCCESSFULLY ===")