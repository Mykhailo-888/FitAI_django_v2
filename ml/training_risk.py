# hjb_fitness_predictor_simple.py
import numpy as np

# --- Функція миттєвої вартості ---
def instant_cost(X, u):
    h, s, b, stress, crp = X
    cost = 0.32*(1 - h/100) + 0.25*max(0,(7.5 - s)/3.5) + 0.18*max(0,(b - 118)/60)
    cost += 0.20*max(0,(stress-5.5)/4.5) + 0.16*max(0,(crp-1.0)/5.0)
    cost += 0.14*u**2 - 0.37*u*(h/90) + 0.15
    return cost

# --- Динаміка стану на 1 день ---
def dynamics(X, u):
    h, s, b, stress, crp = X
    dhrv = -0.025 * u
    dslp = 0.09 * (7.8 - s)
    dbp = 0.045 * u
    # stress та crp залишаються стабільними
    return np.array([h + dhrv, s + dslp, b + dbp, stress, crp])

# --- Основна функція прогнозу risk та optimal u ---
def predict_risk(hrv, sleep, bp, stress=5.0, crp=1.5, days=7):
    # Кліппінг вхідних значень
    hrv = np.clip(float(hrv), 15, 160)
    sleep = np.clip(float(sleep), 3, 12)
    bp = np.clip(float(bp), 90, 200)
    stress = np.clip(float(stress), 1.0, 10.0)
    crp = np.clip(float(crp), 0.1, 20.0)

    X = np.array([hrv, sleep, bp, stress, crp], dtype=float)
    u_values = np.linspace(0,1,21)
    total_costs = []

    # --- Перебір дискретних u ---
    for u in u_values:
        X_sim = X.copy()
        cost = 0.0
        for _ in range(days):
            cost += instant_cost(X_sim, u)
            X_sim = dynamics(X_sim, u)
            # обмеження змінних
            X_sim[0] = np.clip(X_sim[0], 15, 160)
            X_sim[1] = np.clip(X_sim[1], 3, 12)
            X_sim[2] = np.clip(X_sim[2], 90, 190)
        total_costs.append(cost)

    # --- Оптимальна інтенсивність ---
    total_costs = np.array(total_costs)
    opt_idx = np.argmin(total_costs)
    opt_u = u_values[opt_idx]
    risk = np.clip(total_costs[opt_idx]*2.0, 0, 10)

    # --- Текст рекомендації ---
    if risk > 7.5:
        txt = f"Training risk: {risk:.1f}/10. Optimal intensity: {opt_u:.2f}. High risk — light activity only, consult doctor."
    elif risk > 5.0:
        txt = f"Training risk: {risk:.1f}/10. Optimal intensity: {opt_u:.2f}. Elevated risk — reduce load, add recovery days."
    elif risk > 2.5:
        txt = f"Training risk: {risk:.1f}/10. Optimal intensity: {opt_u:.2f}. Moderate risk — monitor HRV and sleep."
    else:
        txt = f"Training risk: {risk:.1f}/10. Optimal intensity: {opt_u:.2f}. Low risk — normal training allowed."

    return risk, txt, opt_u

# --- Тестові випадки ---
if __name__ == "__main__":
    cases = [
        (55, 6.5, 135, 6.2, 5.9),
        (92, 8.1, 112, 3.8, 0.8),
        (32, 5.2, 152, 8.4, 7.1),
        (68, 7.0, 128, 5.1, 2.8)
    ]

    for h, s, b, st, c in cases:
        risk, text, u = predict_risk(h, s, b, st, c)
        print(f"HRV={h}, Sleep={s}, BP={b}, Stress={st}, CRP={c}")
        print(text)
        print("─"*70)