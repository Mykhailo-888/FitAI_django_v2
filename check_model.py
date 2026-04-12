import pickle

filename = r"models/trained_fitness_model_23.pkl"

try:
    with open(filename, 'rb') as f:
        state = pickle.load(f)

    print("Файл завантажено!")
    print("Ключі в файлі:", list(state.keys()))

    if 'mean_X' in state:
        print(f"Кількість ознак (mean_X): {len(state['mean_X'])} (має бути 23)")

    if 'E' in state:
        print(f"Ембеддинг E: shape {state['E'].shape} (має бути (23, 64))")

    print("Модель нормальна.")
except Exception as e:
    print(f"Помилка: {e}")