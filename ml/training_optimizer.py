import numpy as np

def weekly_training_plan_optimizer(
    current_weight=94.0,
    target_weight=88.0,
    weeks_left=12,
    current_hrv=50.0,
    sleep_hours=7.0,
    alcohol_units=0,
    training_load_avg=500,
    age=40,
    systolic_bp=130,
    resting_bpm=70,
    max_hiit_per_week=3
):
    """
    Оптимізований тижневий план тренувань з урахуванням ризиків та стану.
    """
    # Розрахунок ризиків (приклад — додай свої функції hrv_risk, cardio_risk тощо)
    hrv_risk_level = "medium" if current_hrv < 50 else "low"
    cardio_risk_score = 10.0
    if age > 45:
        cardio_risk_score += 6
    if systolic_bp > 135:
        cardio_risk_score += 10
    if alcohol_units > 10:
        cardio_risk_score += 10

    recovery_penalty = 0.0
    sleep_dev = max(0, 7.5 - sleep_hours)
    recovery_penalty += sleep_dev * 0.08
    alcohol_penalty = min(0.25, (alcohol_units / 10.0) ** 1.2 * 0.08)
    load_penalty = min(0.30, np.log1p(training_load_avg / 200.0) * 0.12)
    recovery_penalty += alcohol_penalty + load_penalty
    recovery_penalty = min(0.60, recovery_penalty)

    # Безпечний дефіцит калорій
    kg_to_lose = max(0, current_weight - target_weight)
    kcal_deficit_daily = (kg_to_lose * 7700) / (weeks_left * 7)
    kcal_deficit_daily = np.clip(kcal_deficit_daily, 150, 700)

    # Кількість HIIT з урахуванням ризиків
    hiit_count = max_hiit_per_week
    if recovery_penalty > 0.30 or cardio_risk_score > 60 or current_hrv < 40:
        hiit_count = max(0, hiit_count - 1)
    if recovery_penalty > 0.45 or cardio_risk_score > 75:
        hiit_count = max(0, hiit_count - 1)
    if recovery_penalty > 0.50 or cardio_risk_score > 85:
        hiit_count = 0

    plan = {
        "daily_kcal_deficit": round(kcal_deficit_daily),
        "weekly_hiit_sessions": hiit_count,
        "other_sessions": 7 - hiit_count,
        "estimated_weekly_weight_loss": round(kcal_deficit_daily * 7 / 7700, 2),
        "recovery_penalty_percent": round(recovery_penalty * 100, 1),
        "cardio_risk_score": cardio_risk_score,
        "hrv_risk": hrv_risk_level,
        "hiit_recommendation": "HIIT is allowed" if hiit_count > 0 else "Better to avoid HIIT"
    }

    return plan