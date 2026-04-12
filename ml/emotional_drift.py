import numpy as np

def analyze_emotional_drift(stress_level, alcohol_units=0, days=7, n_sim=10):
    """
    Прогноз емоційного стресу на 7 днів за допомогою стохастичного рівняння Іто.

    Математична модель:
        dS_t = [κ (θ - S_t) + μ S_t + alcohol_drift] dt + σ_eff(S_t) dW_t

    Де:
        S_t          - рівень емоційного стресу в момент t
        θ = 5.5      - довгострокова рівновага (нормальний рівень стресу)
        κ            - швидкість повернення до норми (mean reversion)
        μ            - слабкий природний дрейф
        σ_eff        - ефективна волатильність (залежить від алкоголю)
        alcohol_drift - додатковий дрейф від алкоголю
        dW_t         - приріст Вінерівського процесу (випадковий шум)

    Алкоголь впливає нелінійно: чим більше алкоголю, тим сильніше зростає стрес і нестабільність.
    """
    # Парсинг вхідних даних
    try:
        S = float(stress_level)
    except (TypeError, ValueError):
        S = 5.0

    S = np.clip(S, 1.0, 10.0)
    alcohol = float(alcohol_units)

    if days <= 0:
        return round(S, 1)

    # Параметри моделі
    theta = 5.5
    kappa = 0.13
    mu    = 0.002
    sigma = 0.042

    # Нелінійний вплив алкоголю
    alcohol_norm = min(alcohol / 10.0, 2.5)
    alcohol_effect = 1 / (1 + np.exp(-(alcohol_norm - 1.2)))

    alcohol_drift = alcohol_effect * 0.95          # сильний вплив на рівень стресу
    sigma_eff     = sigma * (1 + 1.8 * alcohol_effect)   # алкоголь робить стрес більш нестабільним

    # Симуляція
    predictions = []
    for _ in range(n_sim):
        current = S
        for _ in range(days):
            dW = np.random.normal(0, 1.0)
            drift = kappa * (theta - current) + mu * current + alcohol_drift
            diffusion = sigma_eff * current * dW
            current += drift + diffusion
            current = np.clip(current, 1.0, 10.0)
        predictions.append(current)

    return round(float(np.mean(predictions)), 1)


# Тест
if __name__ == "__main__":
    print("Stress 5.0, alcohol 0  →", analyze_emotional_drift(5.0, 0))
    print("Stress 5.0, alcohol 5  →", analyze_emotional_drift(5.0, 5))
    print("Stress 5.0, alcohol 12 →", analyze_emotional_drift(5.0, 12))
    print("Stress 5.0, alcohol 25 →", analyze_emotional_drift(5.0, 25))