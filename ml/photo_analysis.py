import cv2
import numpy as np
import os

def measure_width(slice_img):
    """
    Обчислює ширину найбільшого контуру в зрізі.
    Якщо контурів немає — повертає 0.
    """
    contours, _ = cv2.findContours(slice_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return 0

    # Беремо найбільший контур за площею
    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)
    return w


def analyze_body_proportions(photo_path):
    """
    Аналіз пропорцій тіла на фото.
    Повертає словник з результатами або помилкою.
    """
    if not os.path.exists(photo_path):
        return {"error": "Photo not found"}

    img = cv2.imread(photo_path)
    if img is None:
        return {"error": "Cannot read photo"}

    # Preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(blurred, 30, 150)

    # Знаходимо найбільший контур (тіло)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return {"error": "Body not found"}

    largest = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest)

    # Обрізаємо область тіла
    body_edges = edges[y:y + h, x:x + w]

    # Зони вимірювання (відсотки від висоти тіла)
    shoulder_slice = body_edges[int(h * 0.10):int(h * 0.25), :]
    waist_slice   = body_edges[int(h * 0.35):int(h * 0.50), :]
    hip_slice     = body_edges[int(h * 0.60):int(h * 0.80), :]

    # Обчислення ширин
    shoulder_width = measure_width(shoulder_slice)
    waist_width   = measure_width(waist_slice)
    hip_width     = measure_width(hip_slice)

    # Fallback, якщо контур не знайдено в зоні
    if shoulder_width == 0:
        shoulder_width = int(w * 0.75)
    if waist_width == 0:
        waist_width = int(w * 0.55)
    if hip_width == 0:
        hip_width = int(w * 0.85)

    # Ratios
    shoulder_waist_ratio = shoulder_width / waist_width if waist_width > 0 else 1.0
    waist_hip_ratio = waist_width / hip_width if hip_width > 0 else 1.0

    # Класифікація типу фігури
    if shoulder_waist_ratio > 1.35:
        body_type = "V-shape (broad shoulders)"
        rec = "Focus on back and delts 3–4 times per week."
    elif waist_hip_ratio > 0.85:
        body_type = "H-shape (rectangle)"
        rec = "Balance shoulders and waist: strength + cardio."
    elif shoulder_waist_ratio > 1.1 and waist_hip_ratio < 0.8:
        body_type = "X-shape (hourglass)"
        rec = "Keep narrow waist, emphasize core."
    else:
        body_type = "O/A-shape (apple/pear)"
        rec = "Focus on legs and fat loss around waist."

    return {
        "shoulder_width_px": int(shoulder_width),
        "waist_width_px": int(waist_width),
        "hip_width_px": int(hip_width),
        "shoulder_waist_ratio": round(shoulder_waist_ratio, 2),
        "waist_hip_ratio": round(waist_hip_ratio, 2),
        "body_type": body_type,
        "recommendation": rec,
        "error": None,
    }


# Тестовий запуск (тільки при прямому запуску файлу)
if __name__ == "__main__":
    test_photo = r"C:\FitAI_django\media\IMG20230924232928.jpg"
    if os.path.exists(test_photo):
        result = analyze_body_proportions(test_photo)
        print(result)
    else:
        print("Test photo not found")