import pandas as pd
import numpy as np

np.random.seed(42)
print("\n" + 30 * " "  + "FINAL DATASET" + 30 * " ")

original_file = r"C:\FitAI_django\data\gym_members_exercise_tracking.csv"
df = pd.read_csv(original_file)

params_23 = [
    "Age", "Height_cm", "Weight_kg", "Waist_circumference_cm", "Emotional_stress",
    "Alcohol_units_per_week", "Daily_calories_kcal",
    "Max_push_ups", "Max_pull_ups", "Run_1km_min", "Run_100m_sec",
    "Cooper_test_km", "Burpees_3min", "Push_ups_1min", "Sleep_hours",
    "Resting_heart_rate_bpm", "Systolic_blood_pressure_mmhg",
    "Mitochondria_placeholder", "Testosterone_ng_dl", "Cortisol_ug_dl",
    "Hemoglobin_g_dl", "CRP_mg_l", "HRV"
]

df_new = pd.DataFrame(index=df.index, columns=params_23)

# Базові
df_new["Age"] = df["Age"].astype(int)
df_new["Height_cm"] = (df["Height (m)"] * 100).round(0).astype(int)
df_new["Weight_kg"] = df["Weight (kg)"].round(1)
df_new["Resting_heart_rate_bpm"] = np.clip(
    df["Resting_BPM"] + np.random.normal(0, 8, len(df)), 40, 100
).round(0).astype(int)

# Сон — 1 знак
df_new["Sleep_hours"] = np.clip(
    6.5 + np.random.normal(0, 1.2, len(df)),
    4.5, 9.5
).round(1)

# Талія — ціле
df_new["Waist_circumference_cm"] = np.clip(
    80 + np.random.normal(0, 20, len(df)) + 0.4 * (df_new["Weight_kg"] - 70),
    65, 150
).round(0).astype(int)

# Калорії — ціле
gender_offset = np.where(df["Gender"] == "Male", 5, -161)
bmr = 10 * df_new["Weight_kg"] + 6.25 * df_new["Height_cm"] - 5 * df_new["Age"] + gender_offset

# Коефіцієнт активності (1.2 — сидячий, 1.55 — середній, 1.9 — активний)
activity_factor = np.random.normal(1.55, 0.2, len(df))  # середнє 1.55 ±0.2
activity_factor = np.clip(activity_factor, 1.2, 1.9)

# Додаткові калорії від тренувань (200–800 ккал)
workout_calories = np.random.normal(500, 200, len(df))
workout_calories = np.clip(workout_calories, 200, 800)

df_new["Daily_calories_kcal"] = np.clip(
    bmr * activity_factor + workout_calories,
    1600, 5000
).round(0).astype(int)

# Стрес — ціле 1–10
df_new["Emotional_stress"] = np.random.randint(1, 11, len(df))

# Алкоголь — ціле
df_new["Alcohol_units_per_week"] = np.clip(
    0 + 2 * df_new["Emotional_stress"] + np.random.normal(0, 8, len(df)),
    0, 60
).round(0).astype(int)

# Testosterone — 1 знак
df_new["Testosterone_ng_dl"] = np.clip(
    500 + np.random.normal(0, 300, len(df)) - 20 * df_new["Age"] +
    80 * df_new["Sleep_hours"],
    200, 1200
).round(1)

# Cortisol — 1 знак
df_new["Cortisol_ug_dl"] = np.clip(
    10 + 2 * df_new["Emotional_stress"] + np.random.normal(0, 10, len(df)),
    4, 40
).round(1)

# HRV — ціле
df_new["HRV"] = np.clip(
    80 + 25 * df_new["Sleep_hours"] - 15 * df_new["Emotional_stress"] +
    np.random.normal(0, 40, len(df)),
    20, 200
).round(0).astype(int)

# CRP — 1 знак
df_new["CRP_mg_l"] = np.clip(
    0.5 + 0.8 * df_new["Emotional_stress"] + np.random.normal(0, 3, len(df)),
    0.1, 15
).round(1)

# Max_push_ups — ціле
df_new["Max_push_ups"] = np.clip(
    25 + np.random.normal(0, 20, len(df)),
    5, 80
).round(0).astype(int)

# Max_pull_ups — ціле
df_new["Max_pull_ups"] = np.clip(
    8 + np.random.normal(0, 10, len(df)),
    0, 40
).round(0).astype(int)

# Burpees_3min — ціле
df_new["Burpees_3min"] = np.clip(
    50 + np.random.normal(0, 25, len(df)),
    20, 110
).round(0).astype(int)

# Run_1km_min — 1 знак (4–12 хв)
df_new["Run_1km_min"] = np.clip(
    7.0 + np.random.normal(0, 2.5, len(df)),
    4.0, 12.0
).round(1)

# Run_100m_sec — 1 знак (11–20 сек)
df_new["Run_100m_sec"] = np.clip(
    14.0 + np.random.normal(0, 2.0, len(df)),
    11.0, 20.0
).round(1)

# Cooper_test_km — 1 знак (2.0–4.5 км)
df_new["Cooper_test_km"] = np.clip(
    3.0 + np.random.normal(0, 0.8, len(df)),
    2.0, 4.5
).round(1)

# Push_ups_1min — ціле
df_new["Push_ups_1min"] = np.clip(
    df_new["Max_push_ups"] * 0.7 + np.random.normal(0, 12, len(df)),
    5, 80
).round(0).astype(int)

# Systolic — ціле
df_new["Systolic_blood_pressure_mmhg"] = np.clip(
    125 + np.random.normal(0, 15, len(df)),
    105, 170
).round(0).astype(int)

# Hemoglobin — 1 знак
df_new["Hemoglobin_g_dl"] = np.clip(
    14.0 + np.random.normal(0, 2, len(df)),
    11, 18
).round(1)

# Mitochondria — ціле
df_new["Mitochondria_placeholder"] = np.clip(
    200 + np.random.normal(0, 100, len(df)),
    50, 500
).round(0).astype(int)

# Заповнення
df_new = df_new.fillna(df_new.mean(numeric_only=True))

output_file = r"C:\FitAI_django\data\edited_23_params_realistic.csv"
df_new.to_csv(output_file, index=False)

print(f"File: {output_file}")
print( 30 * " " + f"Shape: {df_new.shape}")

print(26 * " " + "=== First 10 lines ===")
print(df_new.head(10).to_string())

print("\n" + 24 * " " + "=== Main statistics (rounded to 1 digit) ===")
key_cols = [
    "Emotional_stress", "Cooper_test_km", "Waist_circumference_cm",
    "Run_1km_min", "Run_100m_sec", "Daily_calories_kcal",
    "Max_push_ups", "Max_pull_ups", "Burpees_3min", "Push_ups_1min",
    "Sleep_hours", "Systolic_blood_pressure_mmhg"
]
stats = df_new[key_cols].describe().loc[['mean', 'std', 'min', 'max']].round(1)
print(stats.to_string())