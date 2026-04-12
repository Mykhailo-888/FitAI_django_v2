import pandas as pd
import numpy as np
import os

input_file = r"C:\FitAI_django\data\edited_23_params_realistic.csv"

if not os.path.exists(input_file):
    print("Error: base dataset not found!")
    print(f"Run first: python ml/preprocess_dataset.py")
    print("After that, run this script again.")
    exit(1)
np.random.seed(42)

print("=== LATENT DATASET (FINAL VERSION — FIXED) ===")

# ─────────────────────────────
# LOAD BASE DATASET
# ─────────────────────────────
input_file = r"C:\FitAI_django\data\edited_23_params_realistic.csv"
df = pd.read_csv(input_file)
df_new = df.copy()

# ─────────────────────────────
# FIX Mitochondria_placeholder — додаємо шум, щоб не було константи 200
# ─────────────────────────────
df_new["Mitochondria_placeholder"] = np.clip(
    df_new["Mitochondria_placeholder"] + np.random.normal(0, 80, len(df)),
    50, 600
).round(0).astype(int)

# ─────────────────────────────
# FIX Cooper_test_km — сильніший шум + зміщена формула
# ─────────────────────────────
df_new["Cooper_test_km"] = np.clip(
    2.5 +  # базове зміщене вгору
    0.7 * df_new["Sleep_hours"] +
    0.6 * (12 - df_new["Run_1km_min"]) +  # швидший біг = кращий Cooper
    -0.02 * df_new["Weight_kg"] +         # слабкий негатив
    np.random.normal(0, 1.0, len(df)),     # сильний шум ±1 км
    2.0, 4.8
).round(1)

# ─────────────────────────────
# LATENT FEATURES — нормалізація компонент ПЕРЕД складанням
# ─────────────────────────────
def normalize(x):
    return (x - np.mean(x)) / (np.std(x) + 1e-8)

# Нормалізуємо всі компоненти
norm_hrv = normalize(df_new["HRV"])
norm_cooper = normalize(df_new["Cooper_test_km"])
norm_mito = normalize(df_new["Mitochondria_placeholder"])
norm_cortisol = normalize(df_new["Cortisol_ug_dl"])
norm_crp = normalize(df_new["CRP_mg_l"])
norm_sleep = normalize(df_new["Sleep_hours"])
norm_stress = normalize(df_new["Emotional_stress"])

# Latent-фічі
latent_energy = (
    0.4 * norm_hrv +
    0.3 * norm_cooper +
    0.3 * norm_mito
)

latent_stress = (
    0.5 * norm_stress +
    0.3 * norm_cortisol +
    0.2 * norm_crp
)

latent_recovery = (
    0.5 * norm_sleep +
    0.3 * norm_hrv -
    0.4 * norm_stress
)

latent_rhythm = np.sin(df_new["Sleep_hours"] / 9 * 2 * np.pi)

# Фінальна нормалізація
df_new["latent_energy"] = normalize(latent_energy)
df_new["latent_stress"] = normalize(latent_stress)
df_new["latent_recovery"] = normalize(latent_recovery)
df_new["latent_rhythm"] = normalize(latent_rhythm)

# ─────────────────────────────
# FINAL CLEAN
# ─────────────────────────────
df_new = df_new.replace([np.inf, -np.inf], np.nan)
df_new = df_new.fillna(df_new.mean(numeric_only=True))

# ─────────────────────────────
# SAVE
# ─────────────────────────────
output_file = r"C:\FitAI_django\data\edited_23_params_realistic_latent.csv"
df_new.to_csv(output_file, index=False)

# ─────────────────────────────
# PRINT
# ─────────────────────────────
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 2000)

print("\n=== DATASET CREATED SUCCESSFULLY ===")
print("File:", output_file)
print("Shape:", df_new.shape)

print("\n=== SAMPLE (first 5 rows) ===")
print(df_new.head().to_string())

print("\n=== STATISTICS (ALL FEATURES, округлено) ===")
print(df_new.describe().loc[['mean', 'std', 'min', 'max']].round(2).to_string())

print("\n=== CHECK (latent means ~0, std ~1) ===")
latent_cols = ["latent_energy", "latent_stress", "latent_recovery", "latent_rhythm"]
print(df_new[latent_cols].describe().loc[['mean', 'std']].round(3).to_string())