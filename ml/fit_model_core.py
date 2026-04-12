import numpy as np
import pickle
import os
from pathlib import Path
from datetime import datetime


class FitnessNeuralNet:
    """
    Нейромережа для прогнозу 8 фітнес-метрик.
    З фізично коректними обмеженнями на виходах + feature importance.
    """

    def __init__(self, lr=0.001, n_iters=20000, embedding_size=48,
                 hidden_size=32, output_size=8, seed=42, momentum=0.9, patience=2000):

        np.random.seed(seed)

        self.lr = lr
        self.n_iters = n_iters
        self.embedding_size = embedding_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.momentum = momentum
        self.patience = patience

        # Ваги
        self.E = None
        self.W1 = None
        self.b1 = None
        self.W_out = None
        self.b_out = None

        # Momentum
        self.v_E = None
        self.v_W1 = None
        self.v_b1 = None
        self.v_W_out = None
        self.v_b_out = None

        # Scaling
        self.mean_X = None
        self.std_X = None
        self.scalers_y = None  # список кортежів (mean, std) для кожного виходу

        # Early stopping
        self.best_val_loss = float('inf')
        self.best_params = None
        self.patience_counter = 0

    # ================= ACTIVATION =================
    def _activation(self, z):
        return np.tanh(z)

    def _activation_derivative(self, a):
        return 1 - a ** 2

    # ================= OUTPUT CONSTRAINTS =================
    def _softplus(self, x):
        """Стабільний softplus"""
        return np.log1p(np.exp(-np.abs(x))) + np.maximum(x, 0)

    def _apply_output_constraints(self, y_raw):
        """Фізичні обмеження на виходи"""
        y = np.zeros_like(y_raw)

        # Calories, Run times, Cooper, Pull-ups, Burpees, 10km, Testosterone → тільки додатні
        for i in [0, 1, 2, 3, 4, 5, 7]:
            y[:, i] = self._softplus(y_raw[:, i])

        # Waist Change → може бути як + так і - (tanh)
        y[:, 6] = np.tanh(y_raw[:, 6]) * 50

        return y

    # ================= FORWARD =================
    def _forward(self, X_norm):
        H = X_norm @ self.E
        a1 = self._activation(H @ self.W1 + self.b1)
        y_raw = a1 @ self.W_out + self.b_out
        y_pred = self._apply_output_constraints(y_raw)
        return y_pred, a1, H, y_raw

    # ================= FIT =================
    def fit(self, X, y, X_val=None, y_val=None, val_every=500):
        X = np.asarray(X, dtype=float)
        y = np.asarray(y, dtype=float)
        n_samples, n_features = X.shape

        # Нормалізація X
        self.mean_X = X.mean(axis=0)
        self.std_X = X.std(axis=0) + 1e-8
        X_norm = (X - self.mean_X) / self.std_X

        # Нормалізація Y (по кожному виходу окремо)
        self.scalers_y = []
        y_norm = np.zeros_like(y)
        for i in range(y.shape[1]):
            mean_i = y[:, i].mean()
            std_i = y[:, i].std() + 1e-8
            self.scalers_y.append((mean_i, std_i))
            y_norm[:, i] = (y[:, i] - mean_i) / std_i

        if X_val is not None and y_val is not None:
            X_val_norm = (X_val - self.mean_X) / self.std_X
            y_val_norm = np.zeros_like(y_val)
            for i in range(y_val.shape[1]):
                mean_i, std_i = self.scalers_y[i]
                y_val_norm[:, i] = (y_val[:, i] - mean_i) / std_i
        else:
            X_val_norm = y_val_norm = None

        # Ініціалізація ваг
        self.E = np.random.randn(n_features, self.embedding_size) * 0.05
        self.W1 = np.random.randn(self.embedding_size, self.hidden_size) * 0.05
        self.b1 = np.zeros(self.hidden_size)
        self.W_out = np.random.randn(self.hidden_size, self.output_size) * 0.05
        self.b_out = np.zeros(self.output_size)

        self.v_E = np.zeros_like(self.E)
        self.v_W1 = np.zeros_like(self.W1)
        self.v_b1 = np.zeros_like(self.b1)
        self.v_W_out = np.zeros_like(self.W_out)
        self.v_b_out = np.zeros_like(self.b_out)

        print(
            f"Training on {n_samples} samples → embedding {self.embedding_size} → hidden {self.hidden_size} → output {self.output_size}")

        for it in range(1, self.n_iters + 1):
            y_pred, a1, H, y_raw = self._forward(X_norm)

            error = y_pred - y_norm
            loss = np.mean(error ** 2)

            # Backpropagation з урахуванням обмежень на виходах
            y_raw_grad = np.ones_like(y_pred)
            for i in [0, 1, 2, 3, 4, 5, 7]:  # softplus
                y_raw_grad[:, i] = 1 / (1 + np.exp(-y_raw[:, i]))
            y_raw_grad[:, 6] = (1 - np.tanh(y_raw[:, 6]) ** 2) * 50  # tanh для талії

            grad_out = (2 * error / n_samples) * y_raw_grad

            grad_W_out = a1.T @ grad_out
            grad_b_out = grad_out.sum(axis=0)

            grad_a1 = grad_out @ self.W_out.T
            grad_z1 = grad_a1 * self._activation_derivative(a1)

            grad_W1 = H.T @ grad_z1
            grad_b1 = grad_z1.sum(axis=0)

            grad_H = grad_z1 @ self.W1.T
            grad_E = X_norm.T @ grad_H

            # Momentum + gradient clipping
            self.v_E = self.momentum * self.v_E - self.lr * np.clip(grad_E, -5, 5)
            self.v_W1 = self.momentum * self.v_W1 - self.lr * np.clip(grad_W1, -5, 5)
            self.v_b1 = self.momentum * self.v_b1 - self.lr * np.clip(grad_b1, -5, 5)
            self.v_W_out = self.momentum * self.v_W_out - self.lr * np.clip(grad_W_out, -5, 5)
            self.v_b_out = self.momentum * self.v_b_out - self.lr * np.clip(grad_b_out, -5, 5)

            self.E += self.v_E
            self.W1 += self.v_W1
            self.b1 += self.v_b1
            self.W_out += self.v_W_out
            self.b_out += self.v_b_out

            # Early stopping
            if X_val_norm is not None:
                y_val_pred, _, _, _ = self._forward(X_val_norm)
                val_loss = np.mean((y_val_pred - y_val_norm) ** 2)

                if val_loss < self.best_val_loss:
                    self.best_val_loss = val_loss
                    self.best_params = {
                        "E": self.E.copy(), "W1": self.W1.copy(), "b1": self.b1.copy(),
                        "W_out": self.W_out.copy(), "b_out": self.b_out.copy()
                    }
                    self.patience_counter = 0
                else:
                    self.patience_counter += 1
                    if self.patience_counter >= self.patience:
                        print(f"Early stopping at iteration {it}")
                        for k, v in self.best_params.items():
                            setattr(self, k, v)
                        break

            if it % val_every == 0 or it == self.n_iters:
                print(f"Iter {it:5d} | Loss: {loss:.6f} | Best val: {self.best_val_loss:.6f}")

        print("Training finished. Best val loss:", self.best_val_loss)

    # ================= PREDICT =================
    def predict(self, X):
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(1, -1)

        X_norm = (X - self.mean_X) / self.std_X
        y_pred_norm, _, _, _ = self._forward(X_norm)

        # Денормалізація
        y_pred = np.zeros_like(y_pred_norm)
        for i in range(y_pred.shape[1]):
            mean_i, std_i = self.scalers_y[i]
            y_pred[:, i] = y_pred_norm[:, i] * std_i + mean_i

        return y_pred

    # ================= FEATURE IMPORTANCE =================
    def feature_importance(self, X, y=None, metric='mae', n_repeats=5):
        """Permutation Feature Importance"""
        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(1, -1)

        if y is None:
            y = self.predict(X)
        y = np.asarray(y, dtype=float)

        baseline_pred = self.predict(X)
        if metric == 'mae':
            baseline_score = np.mean(np.abs(y - baseline_pred))
        else:
            baseline_score = np.mean((y - baseline_pred) ** 2)

        importances = np.zeros(X.shape[1])

        for i in range(X.shape[1]):
            score_diff = 0.0
            for _ in range(n_repeats):
                X_perm = X.copy()
                X_perm[:, i] = np.random.permutation(X_perm[:, i])
                perm_pred = self.predict(X_perm)

                if metric == 'mae':
                    perm_score = np.mean(np.abs(y - perm_pred))
                else:
                    perm_score = np.mean((y - perm_pred) ** 2)

                score_diff += (perm_score - baseline_score)

            importances[i] = score_diff / n_repeats

        importances = np.maximum(importances, 0)
        if importances.sum() > 0:
            importances /= importances.sum()

        return importances

    # ================= SAVE / LOAD =================
    def save_model(self, filename):
        state = {
            "E": self.E,
            "W1": self.W1,
            "b1": self.b1,
            "W_out": self.W_out,
            "b_out": self.b_out,
            "mean_X": self.mean_X,
            "std_X": self.std_X,
            "scalers_y": self.scalers_y,
            "best_val_loss": self.best_val_loss
        }
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, "wb") as f:
            pickle.dump(state, f)
        print(f"✅ Model saved to {filename}")

    def load_model(self, filename):
        with open(filename, "rb") as f:
            state = pickle.load(f)
        self.E = state["E"]
        self.W1 = state["W1"]
        self.b1 = state["b1"]
        self.W_out = state["W_out"]
        self.b_out = state["b_out"]
        self.mean_X = state["mean_X"]
        self.std_X = state["std_X"]
        self.scalers_y = state["scalers_y"]
        self.best_val_loss = state.get("best_val_loss", float('inf'))
        print(f"✅ Model loaded from {filename}")


# ================= HELPER FOR DJANGO =================
def get_fitness_model(dataset_type="simple"):
    """Завантажує модель для використання у Django"""
    model_path = Path(__file__).parent / "models" / f"trained_fitness_model_{dataset_type}.pkl"

    if not model_path.exists():
        print(f"❌ Model file not found: {model_path}")
        print("   Run: python ml/train_model.py first!")
        return None

    model = FitnessNeuralNet()
    model.load_model(str(model_path))
    return model