# tests/test_views.py
import pytest
from fitness.views import validate_input


def test_validate_input_valid_float():
    """Коректне float значення"""
    val, err = validate_input("178.5", "float", "Height")
    assert val == 178.5
    assert err is None


def test_validate_input_invalid_number():
    """Некоректне число (рядок замість числа)"""
    val, err = validate_input("abc", "int", "Emotional stress")
    assert val is None
    assert err is not None


def test_validate_input_out_of_range():
    """Значення поза дозволеним діапазоном"""
    val, err = validate_input("150", "int", "Alcohol (units/week)")
    assert val is None
    assert err is not None
    assert "between 0 and 100" in err


def test_validate_input_empty_required():
    """Порожнє значення для обов'язкового поля"""
    val, err = validate_input("", "int", "Emotional stress")
    assert val is None
    assert err is not None


def test_validate_input_none_input():
    """Передача None як значення"""
    val, err = validate_input(None, "float", "Sleep")
    assert val is None
    assert err is not None


def test_validate_input_valid_alcohol():
    """Коректне значення алкоголю"""
    val, err = validate_input("5", "int", "Alcohol (units/week)")
    assert val == 5
    assert err is None