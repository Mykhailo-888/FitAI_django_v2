import pickle
from pathlib import Path

# Correct path - model is located in ml/models/
model_path = Path(r"C:\FitAI_django\ml\models\trained_fitness_model_simple.pkl")

print(f"Checking file: {model_path}")
print(f"File exists: {model_path.exists()}\n")

if model_path.exists():
    with open(model_path, 'rb') as f:
        state = pickle.load(f)

    print("=== CONTENT OF .pkl FILE ===\n")

    for key, value in state.items():
        print(f"Key: {key}")

        if hasattr(value, 'shape'):
            print(f"   → shape = {value.shape}   (type: {type(value).__name__})")
        elif isinstance(value, list) and value and hasattr(value[0], 'shape'):
            print(f"   → list with {len(value)} elements")
            for i, item in enumerate(value[:3]):   # show only first 3
                print(f"     [{i}]: shape = {item.shape}")
            if len(value) > 3:
                print(f"     ... and {len(value) - 3} more layers")
        elif isinstance(value, (int, float)):
            print(f"   → {value}")
        else:
            print(f"   → type = {type(value).__name__}, length = {len(value) if hasattr(value, '__len__') else 'N/A'}")

        print("-" * 50)
else:
    print("File not found at this path!")
    print("Check if trained_fitness_model_simple.pkl really exists in ml\\models\\")