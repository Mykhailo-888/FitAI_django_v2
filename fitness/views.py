# fitness/views.py — ФІНАЛЬНА ВИПРАВЛЕНА ВЕРСІЯ
from pathlib import Path
import os
import json
import numpy as np
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.files.storage import default_storage
from django.conf import settings

from .models import UserData
from ml.fit_model_core import get_fitness_model
from ml.training_optimizer import weekly_training_plan_optimizer
from ml.emotional_drift import analyze_emotional_drift
from ml.training_risk import predict_risk
from ml.photo_analysis import analyze_body_proportions

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
# -----------------------------
# Helper: validate numeric input
# -----------------------------
def validate_input(value, dtype, question):
    try:
        if dtype == "int":
            val = int(value)
        elif dtype == "float":
            val = float(value)
        else:
            return value, None
    except (ValueError, TypeError):
        return None, f"Invalid number format for {question}"

    ranges = {
        "Age": (16, 100), "Height": (100, 250), "Weight": (30, 300),
        "Waist circumference": (40, 200), "Emotional stress": (1, 10),
        "Alcohol (units/week)": (0, 100), "Max push-ups": (0, 500),
        "Max pull-ups": (0, 100), "1 km run": (3, 30), "100 m run": (10, 60),
        "Cooper test": (1, 20), "Burpees in 3 min": (0, 200),
        "Push-ups in 1 min": (0, 100), "Sleep": (0, 24),
        "Resting heart rate": (30, 120), "Systolic blood pressure": (80, 200),
        "HRV": (0, 200), "Mitochondria (placeholder)": (0, 1000),
        "Testosterone": (0, 2000), "Cortisol": (0, 100),
        "Hemoglobin": (0, 25), "CRP": (0, 100)
    }

    if question in ranges:
        min_val, max_val = ranges[question]
        if not (min_val <= val <= max_val):
            return None, f"{question} must be between {min_val} and {max_val}"

    return val, None


# -----------------------------
# Onboarding view
# -----------------------------
def onboarding(request):
    questions = [
        ("Age", "years", "int", True),
        ("Height", "cm", "float", True),
        ("Weight", "kg", "float", True),
        ("Upload photo for body proportions analysis", "photo", "photo", False),
        ("Waist circumference", "cm", "float", False),
        ("Emotional stress", "1-10", "int", False),
        ("Alcohol (units/week)", "units", "int", False),
        ("Daily calories (kcal/day)", "kcal", "float", False),
        ("Max push-ups", "reps", "int", False),
        ("Max pull-ups", "reps", "int", False),
        ("1 km run", "min", "float", False),
        ("100 m run", "sec", "float", False),
        ("Cooper test", "km", "float", False),
        ("Burpees in 3 min", "reps", "int", False),
        ("Push-ups in 1 min", "reps", "int", False),
        ("Sleep", "hours/day", "float", False),
        ("Resting heart rate", "BPM", "int", False),
        ("HRV", "units", "int", False),
        ("Systolic blood pressure", "mmHg", "int", False),
        ("Mitochondria (placeholder)", "units", "float", False),
        ("Testosterone", "ng/dL", "float", False),
        ("Cortisol", "μg/dL", "float", False),
        ("Hemoglobin", "g/dL", "float", False),
        ("CRP", "mg/L", "float", False),
    ]

    current_index = int(request.GET.get('q', 0))

    # Ініціалізуємо onboarding_data, якщо його немає
    if 'onboarding_data' not in request.session:
        request.session['onboarding_data'] = {}

    if request.method == 'POST':
        question, unit, dtype, required = questions[current_index]
        value = None
        error = None

        if dtype == "photo":
            uploaded_file = request.FILES.get(f'answer_{current_index}')
            if uploaded_file:
                relative_path = default_storage.save(f"photos/{uploaded_file.name}", uploaded_file)
                value = relative_path
        else:
            raw_value = request.POST.get(f'answer_{current_index}')
            if raw_value:
                value, error = validate_input(raw_value, dtype, question)
            elif required:
                error = f"{question} is required"

        if error:
            context = {
                'question': question,
                'unit': unit,
                'dtype': dtype,
                'required': required,
                'current_index': current_index,
                'total_questions': len(questions),
                'is_first': current_index == 0,
                'error': error,
                'previous_value': request.POST.get(f'answer_{current_index}', ''),
                'placeholder_text': "Enter your answer",
            }
            return render(request, 'onboarding.html', context)

        # Зберігаємо в окремий ключ onboarding_data
        request.session['onboarding_data'][question] = value
        print(f"SAVED TO ONBOARDING_DATA: {question} = {value}")
        request.session.modified = True

        next_index = current_index + 1
        if next_index >= len(questions):
            return process_onboarding_results(request)

        return redirect(reverse('onboarding') + f'?q={next_index}')

    # ====================== GET (показ форми) ======================
    question, unit, dtype, required = questions[current_index]

    # Безпечне отримання даних
    onboarding_data = request.session.get('onboarding_data', {})
    previous_value = onboarding_data.get(question, '')

    # ====================== PLACEHOLDER TEXT ======================
    placeholder_text = "Enter your answer"

    q_lower = question.lower()

    if "emotional stress" in q_lower:
        placeholder_text = "e.g. 6 (1-10)"
    elif "alcohol" in q_lower:
        placeholder_text = "e.g. 5"
    elif question == "Age":
        placeholder_text = "e.g. 28"
    elif question == "Height":
        placeholder_text = "e.g. 175"
    elif question == "Weight":
        placeholder_text = "e.g. 75"
    elif question == "Waist circumference":
        placeholder_text = "e.g. 90"
    elif question == "Sleep":
        placeholder_text = "e.g. 7.5"
    elif "crp" in q_lower:
        placeholder_text = "e.g. 1.5"
    elif "blood pressure" in q_lower:
        placeholder_text = "e.g. 120"
    elif "heart rate" in q_lower or "hrv" in q_lower:
        placeholder_text = "e.g. 70"
    elif "daily calories" in q_lower:
        placeholder_text = "e.g. 2500"
    elif "max push-ups" in q_lower:
        placeholder_text = "e.g. 20"
    elif "max pull-ups" in q_lower:
        placeholder_text = "e.g. 8"
    elif "1 km run" in q_lower:
        placeholder_text = "e.g. 6.0"
    elif "100 m run" in q_lower:
        placeholder_text = "e.g. 15"
    elif "cooper test" in q_lower:
        placeholder_text = "e.g. 2.8"
    elif "burpees in 3 min" in q_lower:
        placeholder_text = "e.g. 40"
    elif "push-ups in 1 min" in q_lower:
        placeholder_text = "e.g. 30"
    elif "testosterone" in q_lower:
        placeholder_text = "e.g. 500"
    elif "cortisol" in q_lower:
        placeholder_text = "e.g. 15"
    elif "hemoglobin" in q_lower:
        placeholder_text = "e.g. 14.5"
    elif "mitochondria" in q_lower:
        placeholder_text = "e.g. 50"

    context = {
        'question': question,
        'unit': unit,
        'dtype': dtype,
        'required': required,
        'current_index': current_index,
        'total_questions': len(questions),
        'is_first': current_index == 0,
        'previous_value': previous_value,
        'placeholder_text': placeholder_text,
    }

    return render(request, 'onboarding.html', context)


# -----------------------------
# Process final onboarding results
# -----------------------------
def process_onboarding_results(request):
    try:
        # Беремо дані з правильного ключа
        data = request.session.get('onboarding_data', {}).copy()
        print("ONBOARDING DATA RECEIVED:", data)

        defaults = {
            "Age": 30, "Height": 175, "Weight": 75, "Waist circumference": 90,
            "Emotional stress": 5, "Alcohol (units/week)": 0, "Daily calories (kcal/day)": 2500,
            "Max push-ups": 20, "Max pull-ups": 8, "1 km run": 6.0, "100 m run": 15.0,
            "Cooper test": 2.8, "Burpees in 3 min": 40, "Push-ups in 1 min": 30,
            "Sleep": 7.0, "Resting heart rate": 70, "HRV": 70, "Systolic blood pressure": 120,
            "Mitochondria (placeholder)": 50, "Testosterone": 500, "Cortisol": 15.0,
            "Hemoglobin": 14.5, "CRP": 1.5
        }

        for key, val in defaults.items():
            if key not in data or data.get(key) in (None, '', 'None', None):
                data[key] = val

        crp = float(data.get("CRP", 1.5))
        initial_stress = float(data.get("Emotional stress", 5.0))
        alcohol_units = float(data.get("Alcohol (units/week)", 0.0))
        hrv = float(data.get("HRV", 70.0))
        sleep = float(data.get("Sleep", 7.0))
        bp = float(data.get("Systolic blood pressure", 120.0))

        recommendations = []

        # ====================== PHOTO ANALYSIS ======================
        photo_path = data.get("Upload photo for body proportions analysis")
        if photo_path:
            absolute_path = os.path.join(settings.MEDIA_ROOT, photo_path)
            if os.path.exists(absolute_path):
                try:
                    proportions = analyze_body_proportions(absolute_path)
                    if proportions and proportions.get("error") is None:
                        photo_rec = proportions.get('recommendation', "").strip()
                        if photo_rec:
                            recommendations.append(photo_rec)
                except Exception as e:
                    recommendations.append(f"Photo analysis error: {str(e)}")

        # ====================== EMOTIONAL DRIFT ======================
        try:
            predicted_stress = analyze_emotional_drift(initial_stress, alcohol_units, days=7)
        except:
            predicted_stress = initial_stress

        # ====================== WEEKLY TRAINING PLAN ======================
        weekly_plan = weekly_training_plan_optimizer(
            current_weight=float(data.get("Weight", 75)),
            target_weight=70.0,
            weeks_left=1,
            current_hrv=hrv,
            sleep_hours=sleep,
            alcohol_units=alcohol_units,
            training_load_avg=float(data.get("Daily calories (kcal/day)", 2500)),
            age=float(data.get("Age", 30)),
            systolic_bp=bp,
            resting_bpm=float(data.get("Resting heart rate", 70))
        )

        # ====================== CRP ======================
        if crp >= 5.0:
            weekly_plan['weekly_hiit_sessions'] = 0
            weekly_plan['other_sessions'] = 0
            weekly_plan['hiit_recommendation'] = "Better to avoid HIIT"

            recommendations.append(f"CRITICAL! CRP = {crp:.1f} mg/L — severe inflammation.")
            recommendations.append("NO TRAINING ALLOWED this week!")
            recommendations.append("URGENT: See a doctor immediately.")
            recommendations.append("Do not train until you get medical clearance.")
        else:
            weekly_plan['hiit_recommendation'] = "HIIT is allowed"

            try:
                risk_score, risk_text, optimal_intensity = predict_risk(hrv, sleep, bp, predicted_stress, crp)
            except:
                risk_score, risk_text, optimal_intensity = 5.0, "Moderate risk", 1.0

            recommendations.append(f"CRP = {crp:.1f} mg/L — within normal range.")
            recommendations.append(risk_text)
            recommendations.append(f"Recommended training intensity: {optimal_intensity * 100:.0f}% of maximum")

            if optimal_intensity >= 0.85:
                recommendations.append("You can train at high intensity this week.")
            else:
                recommendations.append("Moderate training is recommended.")

        if predicted_stress >= 7.0:
            recommendations.append(
                f"Predicted emotional stress after 7 days: {predicted_stress:.1f} (initial was {initial_stress:.1f})")
            recommendations.append(
                "Prioritize sleep, meditation/breathing exercises (10-15 min daily), and light walks.")

        if sleep < 6.5:
            recommendations.append("Insufficient sleep detected. Aim for 7.5–8.5 hours nightly.")

        if hrv < 50:
            recommendations.append("Low HRV indicates poor recovery. Consider adding an extra rest day.")

        recommendations_text = "\n".join([f"• {rec}" for rec in recommendations])

        # ====================== FEATURE IMPACT ======================
        feature_impact = []

        try:
            explain_path = Path(settings.BASE_DIR) / "ml" / "feature_importance.json"
            if explain_path.exists():
                with open(explain_path, "r", encoding="utf-8") as f:
                    explain_data = json.load(f)

                for out_name, out_data in explain_data.get("per_output", {}).items():
                    features = out_data.get("features", [])
                    rel = out_data.get("relative_percent", [])
                    grad = out_data.get("gradient_percent", [])

                    relative_list = []
                    gradient_list = []

                    for i in range(min(6, len(features))):
                        feature = features[i].replace('_', ' ')
                        feature = feature.replace('ng dl', 'ng/dL').replace('mmhg', 'mmHg').replace('mg l', 'mg/L')

                        rel_val = float(rel[i]) if i < len(rel) else 0.0
                        grad_val = float(grad[i]) if i < len(grad) else 0.0

                        relative_list.append({"name": feature, "value": round(rel_val, 1)})
                        gradient_list.append({"name": feature, "value": round(grad_val, 1)})

                    feature_impact.append({
                        "output": out_name.upper().replace('_', ' '),
                        "relative": relative_list,
                        "gradient": gradient_list
                    })

        except Exception as e:
            print("Feature impact error:", e)

        # ====================== FORMAT PLAN ======================
        weekly_plan_formatted = {
            k.replace("_", " ").title(): round(v, 2) if isinstance(v, (float, np.float64)) else v
            for k, v in weekly_plan.items()
        }

        # ====================== NEURAL NET PREDICTION ======================
        PREDICTION_LABELS = [
            ("Calories Burned", "kcal"), ("1 km Run Time", "min"), ("Cooper Test Distance", "km"),
            ("Max Pull-Ups", "reps"), ("Burpees per Hour", "reps"), ("10 km Run Time", "min"),
            ("Waist Circumference Change", "cm"), ("Testosterone Level", "ng/dL")
        ]

        model_error = None
        pred = None
        explainability = []

        try:
            model = get_fitness_model("simple")
            if model is None:
                raise ValueError("Модель не завантажена. Запустіть: python ml/train_model.py")

            all_features = [
                "Age", "Height", "Weight", "Waist circumference", "Emotional stress",
                "Alcohol (units/week)", "Daily calories (kcal/day)",
                "Max push-ups", "Max pull-ups", "1 km run", "100 m run",
                "Cooper test", "Burpees in 3 min", "Push-ups in 1 min", "Sleep",
                "Resting heart rate", "Systolic blood pressure",
                "Mitochondria (placeholder)", "Testosterone", "Cortisol",
                "Hemoglobin", "CRP", "HRV"
            ]

            data_values = [float(data.get(f, defaults.get(f, 0))) for f in all_features]
            print("INPUT FEATURES TO MODEL:", data_values)

            data_array = np.array(data_values).reshape(1, -1)
            pred = model.predict(data_array)

            try:
                base_pred = pred[0].copy()
                impacts = []
                for i in range(len(data_values)):
                    modified = data_array.copy()
                    modified[0, i] *= 1.20
                    new_pred = model.predict(modified)[0]
                    impact = float(np.mean(np.abs(new_pred - base_pred)))
                    impacts.append((all_features[i], impact))
                impacts.sort(key=lambda x: x[1], reverse=True)
                explainability = impacts[:6]
            except:
                explainability = []

        except Exception as e:
            model_error = f"Не вдалося отримати передбачення: {type(e).__name__} – {str(e)}"
            pred = np.zeros((1, 8))
            explainability = []

        prediction_with_labels = []
        for i, (label, unit) in enumerate(PREDICTION_LABELS):
            try:
                value = float(pred[0, i]) if isinstance(pred, np.ndarray) and pred.size > i else 0.0
                value = round(value) if label in ["Calories Burned", "Max Pull-Ups", "Burpees per Hour"] else round(
                    value, 1)
            except:
                value = 0.0
            prediction_with_labels.append((label, unit, value))

        prediction_list = pred[0].tolist() if isinstance(pred, np.ndarray) and pred.ndim == 2 else [0.0] * 8

        # Зберігаємо в базу
        UserData.objects.create(
            age=float(data.get("Age", 30)),
            height_cm=float(data.get("Height", 175)),
            weight_kg=float(data.get("Weight", 75)),
            waist_circumference_cm=float(data.get("Waist circumference", 90)),
            emotional_stress=predicted_stress,
            alcohol_units_per_week=alcohol_units,
            daily_calories_kcal=float(data.get("Daily calories (kcal/day)", 2500)),
            max_push_ups=int(data.get("Max push-ups", 20)),
            max_pull_ups=int(data.get("Max pull-ups", 8)),
            run_1km_min=float(data.get("1 km run", 6.0)),
            run_100m_sec=float(data.get("100 m run", 15.0)),
            cooper_test_km=float(data.get("Cooper test", 2.8)),
            burpees_3min=int(data.get("Burpees in 3 min", 40)),
            push_ups_1min=int(data.get("Push-ups in 1 min", 30)),
            sleep_hours=float(data.get("Sleep", 7.0)),
            resting_heart_rate_bpm=int(data.get("Resting heart rate", 70)),
            hrv=hrv,
            systolic_blood_pressure_mmhg=bp,
            mitochondria_placeholder=float(data.get("Mitochondria (placeholder)", 50)),
            testosterone_ng_dl=float(data.get("Testosterone", 500)),
            cortisol_ug_dl=float(data.get("Cortisol", 15.0)),
            hemoglobin_g_dl=float(data.get("Hemoglobin", 14.5)),
            crp_mg_l=crp,
            prediction=prediction_list,
            weekly_plan=weekly_plan
        )

        # Очищаємо тільки дані онбордингу
        request.session.pop('onboarding_data', None)
        request.session.modified = True

        return render(request, 'results.html', {
            'prediction_with_labels': prediction_with_labels,
            'weekly_plan': weekly_plan_formatted,
            'recommendations': recommendations_text,
            'model_error': model_error,
            'explainability': explainability,
            'feature_impact': feature_impact
        })

    except Exception as e:
        print("!!! CRITICAL ERROR in process_onboarding_results:", str(e))
        return render(request, 'results.html', {
            'prediction_with_labels': [("Error", "", 0)] * 8,
            'weekly_plan': {},
            'recommendations': f"Помилка обробки даних:\n• {str(e)}",
            'model_error': f"CRITICAL ERROR: {str(e)}",
            'explainability': [],
            'feature_impact': []
        })


# --------------------- OTHER VIEWS ---------------------
def update_data(request):
    if request.method == 'POST':
        return redirect('onboarding')
    return render(request, 'update.html', {})


def history(request):
    records = UserData.objects.order_by('-timestamp')[:30]
    chart_timestamps = []
    chart_data = {k: [] for k in ['calories', 'run1km', 'cooper', 'pullups', 'burpees', 'run10km', 'waist_ch', 'testo']}
    forecast_data = []

    for r in records:
        chart_timestamps.append(r.timestamp.strftime('%d.%m.%Y %H:%M') if r.timestamp else '—')
        pred = r.prediction
        if isinstance(pred, str):
            try:
                pred = json.loads(pred)
            except:
                pred = None
        if isinstance(pred, (list, tuple)) and len(pred) == 1 and isinstance(pred[0], (list, tuple)):
            pred = pred[0]
        values = pred if pred else [None] * 8

        forecast_data.append(values)
        chart_data['calories'].append(float(values[0]) if values[0] is not None else None)
        chart_data['run1km'].append(float(values[1]) if values[1] is not None else None)
        chart_data['cooper'].append(float(values[2]) if values[2] is not None else None)
        chart_data['pullups'].append(float(values[3]) if values[3] is not None else None)
        chart_data['burpees'].append(float(values[4]) if values[4] is not None else None)
        chart_data['run10km'].append(float(values[5]) if values[5] is not None else None)
        chart_data['waist_ch'].append(float(values[6]) if values[6] is not None else None)
        chart_data['testo'].append(float(values[7]) if values[7] is not None else None)

    context = {
        'records': records,
        'timestamps_json': json.dumps(chart_timestamps),
        **{f"{k}_json": json.dumps(v) for k, v in chart_data.items()},
        'record_count': len(records),
        'forecast_data': forecast_data,
        'photo_recommendation': "No photo analysis available",
    }
    return render(request, 'history.html', context)

def training_log_view(request):
    feature_file = Path(r"C:/FitAI_django/ml/feature_importance.json")
    training_file = Path(r"C:/FitAI_django/ml/training_history.json")

    features = {}
    history = {}

    if feature_file.exists():
        with open(feature_file, "r", encoding="utf-8") as f:
            features = json.load(f)

    if training_file.exists():
        with open(training_file, "r", encoding="utf-8") as f:
            history = json.load(f)

    return render(request, "training_log.html", {
        "features": features,
        "history": history,
    })

def metrics(request):
    records = list(UserData.objects.order_by('timestamp'))

    param_names = [
        "Calories Burned", "1 km Run Time", "Cooper Test", "Max Pull-Ups",
        "Burpees", "10 km Run Time", "Waist Change", "Testosterone"
    ]

    if len(records) < 2:
        return render(request, 'metrics.html', {
            'results': {},
            'warning': 'Not enough data'
        })

    last_pred = records[-1].prediction

    if isinstance(last_pred, list) and len(last_pred) == 1:
        last_pred = last_pred[0]

    results = {}

    for i in range(8):

        prev_vals = []

        for rec in records[:-1]:
            pred = rec.prediction

            if isinstance(pred, list) and len(pred) == 1:
                pred = pred[0]

            if pred and len(pred) > i and pred[i] is not None:
                prev_vals.append(float(pred[i]))

        current = float(last_pred[i])

        # =========================
        # STABILITY (FIXED / NORMALIZED)
        # =========================

        prev_vals = []

        for rec in records[:-1]:
            pred = rec.prediction

            if isinstance(pred, list) and len(pred) == 1:
                pred = pred[0]

            if pred and len(pred) > i and pred[i] is not None:
                prev_vals.append(float(pred[i]))

        current = float(last_pred[i])

        if len(prev_vals) >= 2:
            arr = np.array(prev_vals)

            stability_mean = float(np.mean(arr))
            stability_std = float(np.std(arr))

            # 🔥 ВАЖЛИВО: нормалізований drift (КЛЮЧ ДО ВСЬОГО)
            stability_drift = abs(current - stability_mean) / (stability_std + 1e-8)

        else:
            stability_mean = 0.0
            stability_std = 0.0
            stability_drift = 0.0

        # =========================
        # SYNTHETIC
        # =========================
        syn_vals = []

        for rec in records:
            x = {
                "sleep": float(getattr(rec, 'sleep_hours', 7.0)),
                "hrv": float(getattr(rec, 'hrv', 70.0)),
                "stress": float(getattr(rec, 'emotional_stress', 5.0)),
                "weight": float(getattr(rec, 'weight_kg', 75.0)),
            }

            syn_vals.append(synthetic_ground_truth(x, i))

        syn_vals = np.array(syn_vals)

        synthetic_mean = float(np.mean(syn_vals))
        synthetic_std = float(np.std(syn_vals))
        synthetic_drift = abs(current - synthetic_mean) / (synthetic_std + 1e-8)

        # =========================
        # MODEL HEALTH SCORE
        # =========================
        stability_penalty = min(stability_drift * 2 + stability_std * 3, 100)
        synthetic_penalty = min(synthetic_drift * 1.5, 100)

        model_health_score = 100 - (0.6 * stability_penalty + 0.4 * synthetic_penalty)
        model_health_score = max(0, min(100, model_health_score))

        # =========================
        # SAVE
        # =========================
        results[param_names[i]] = {
            "last_pred": round(current, 2),
            "count": len(prev_vals),

            # stability
            "stability_mean": round(stability_mean, 2),
            "stability_std": round(stability_std, 2),
            "stability_drift": round(stability_drift, 2),

            # synthetic
            "synthetic_mean": round(synthetic_mean, 2),
            "synthetic_std": round(synthetic_std, 2),
            "synthetic_drift": round(synthetic_drift, 2),

            # ⭐ FINAL SCORE
            "model_health_score": round(model_health_score, 1),
        }

    return render(request, 'metrics.html', {
        'results': results,
        'warning': 'Model Stability + Synthetic Simulation + Health Score'
    })

def synthetic_ground_truth(x, i):
    """Проста, але стабільна synthetic функція"""
    sleep = x.get("sleep", 7.0)
    hrv = x.get("hrv", 70.0)
    stress = x.get("stress", 5.0)
    crp = x.get("crp", 1.5)
    weight = x.get("weight", 75.0)

    if i == 0:  # Calories Burned
        return 1800 + sleep * 80 + hrv * 8 - stress * 60 - crp * 30
    elif i == 1:  # 1km Run
        return 9.0 - (hrv / 15) + (stress / 4)
    elif i == 2:  # Cooper Test
        return 2.7 + (hrv / 30) - (stress / 8)
    elif i == 3:  # Pull-ups
        return 8 + (weight / 12) - (stress * 0.8)
    elif i == 4:  # Burpees
        return 55 + hrv * 1.2 - stress * 4
    elif i == 5:  # 10km Run
        return 65 + stress * 1.5 - (hrv / 2)
    elif i == 6:  # Waist Change
        return -2.5 - sleep * 0.6 + stress * 0.4 + (weight - 75) * 0.08
    elif i == 7:  # Testosterone
        return 380 + sleep * 18 - stress * 22 + (hrv / 3)

    return 0.0