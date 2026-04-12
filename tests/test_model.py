# tests/test_model.py
import pytest
import numpy as np
from ml.fit_model_core import FitnessNeuralNet

# Базовий вхід (23 параметри) — використовуємо типові дефолтні значення
@pytest.fixture
def base_input():
    return np.array([[
        30,      # Age
        175,     # Height cm
        75,      # Weight kg
        90,      # Waist cm
        5,       # Emotional stress
        0,       # Alcohol units/week
        2500,    # Daily calories
        20,      # Max push-ups
        8,       # Max pull-ups
        6.0,     # 1 km run min
        15.0,    # 100 m run sec
        2.8,     # Cooper test km
        40,      # Burpees in 3 min
        30,      # Push-ups in 1 min
        7.0,     # Sleep hours
        70,      # Resting heart rate BPM
        120,     # Systolic BP mmHg
        50,      # Mitochondria placeholder
        500,     # Testosterone ng/dL
        15.0,    # Cortisol μg/dL
        14.5,    # Hemoglobin g/dL
        1.5,     # CRP mg/L
        70       # HRV
    ]], dtype=float)


@pytest.fixture
def model():
    m = FitnessNeuralNet()
    m.load_model("ml/models/trained_fitness_model_simple.pkl")
    return m


def test_model_predicts_something(model, base_input):
    pred = model.predict(base_input)
    assert pred.shape == (1, 8), "Prediction shape must be (1, 8)"
    assert not np.all(pred == 0), "Prediction should not be all zeros"


def test_increased_sleep_improves_prediction(model, base_input):
    base_pred = model.predict(base_input)[0]

    # Збільшуємо Sleep з 7.0 до 9.0 (індекс 14)
    improved_input = base_input.copy()
    improved_input[0, 14] = 9.0

    improved_pred = model.predict(improved_input)[0]

    # Очікуємо покращення хоча б одного з позитивних показників
    assert improved_pred[0] > base_pred[0] or improved_pred[7] > base_pred[7], \
        "Increased sleep should improve Calories Burned or Testosterone"


def test_increased_CRP_worsens_prediction(model, base_input):
    base_pred = model.predict(base_input)[0]

    # Збільшуємо CRP з 1.5 до 6.0 (індекс 21)
    bad_input = base_input.copy()
    bad_input[0, 21] = 6.0

    bad_pred = model.predict(bad_input)[0]

    # Очікуємо погіршення хоча б одного показника (наприклад Cooper Test нижче, або Run Time довше)
    assert bad_pred[2] < base_pred[2] or bad_pred[1] > base_pred[1], \
        "High CRP should worsen Cooper Test or 1 km Run Time"


def test_model_output_range_sensible(model, base_input):
    pred = model.predict(base_input)[0]

    # Calories (виглядає як денний рівень / TDEE)
    assert 1500 < pred[0] < 3500, f"Calories unrealistic: {pred[0]}"

    # 1 km Run Time (хвилини)
    assert 3 < pred[1] < 12, f"1 km run time unrealistic: {pred[1]}"

    # Max Pull-Ups
    assert 0 <= pred[3] <= 50, f"Pull-ups unrealistic: {pred[3]}"


def test_model_deterministic(model, base_input):
    pred1 = model.predict(base_input)
    pred2 = model.predict(base_input)
    assert np.allclose(pred1, pred2), "Model should be deterministic (same input = same output)"
def test_weight_increase_raises_calories(model, base_input):
    base_pred = model.predict(base_input)[0]

    # збільшуємо вагу з 75 → 90 кг (індекс 2)
    heavier_input = base_input.copy()
    heavier_input[0, 2] = 90

    heavier_pred = model.predict(heavier_input)[0]

    assert heavier_pred[0] > base_pred[0], \
        "Higher weight should increase Calories Burned"
def test_high_heart_rate_reduces_endurance(model, base_input):
    base_pred = model.predict(base_input)[0]

    # збільшуємо пульс з 70 → 90 (індекс 15)
    bad_input = base_input.copy()
    bad_input[0, 15] = 90

    bad_pred = model.predict(bad_input)[0]

    assert bad_pred[2] < base_pred[2], \
        "Higher resting heart rate should reduce endurance (Cooper test)"


def test_strong_sleep_decrease_worsens_metrics(model, base_input):
    base_pred = model.predict(base_input)[0]

    bad_input = base_input.copy()
    bad_input[0, 14] = 4.0  # Sleep 4 години

    bad_pred = model.predict(bad_input)[0]

    assert bad_pred[0] < base_pred[0] or bad_pred[7] < base_pred[7] or bad_pred[2] < base_pred[2], \
        "Strong sleep decrease should worsen multiple metrics"


def test_combined_poor_recovery(model, base_input):
    """Комбінований поганий стан: низький сон + низький HRV + високий стрес"""
    base_pred = model.predict(base_input)[0]

    bad_input = base_input.copy()
    bad_input[0, 14] = 4.5  # Sleep
    bad_input[0, 22] = 35  # HRV
    bad_input[0, 4] = 9  # Emotional stress

    bad_pred = model.predict(bad_input)[0]

    assert bad_pred[6] < base_pred[6] or bad_pred[7] < base_pred[7], \
        "Poor recovery state should negatively affect waist/testosterone"