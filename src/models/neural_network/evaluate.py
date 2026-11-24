from pathlib import Path

import joblib
import pandas as pd
import torch
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    roc_auc_score,
)

from src.models.neural_network.model import CreditScoringNN


# Пути к данным и модели
ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models" / "neural_network"

TARGET = "default.payment.next.month"

# Загружаем тестовую выборку
df = pd.read_csv(DATA_DIR / "test.csv")

X_test = df.drop(columns=TARGET)
y_test = df[TARGET]

# Применяем сохранённую предобработку
preprocessor = joblib.load(MODEL_DIR / "preprocessor.joblib")
X_test = preprocessor.transform(X_test)

X_test = torch.tensor(X_test, dtype=torch.float32)

# Загружаем обученную модель
model = CreditScoringNN(input_dim=X_test.shape[1])
model.load_state_dict(
    torch.load(MODEL_DIR / "best_model.pth", map_location="cpu", weights_only=True)
)
model.eval()

# Получаем вероятности дефолта
with torch.no_grad():
    logits = model(X_test)
    probabilities = torch.sigmoid(logits).numpy().ravel()

# Преобразуем вероятности в классы
predictions = (probabilities >= 0.5).astype(int)

# Оцениваем качество модели
print(f"Test ROC-AUC: {roc_auc_score(y_test, probabilities):.4f}")
print(f"Test PR-AUC (AP): {average_precision_score(y_test, probabilities):.4f}")

print("\nClassification report:")
print(classification_report(y_test, predictions, digits=4))


# Сохраняем метрики для последующего сравнения
results = pd.DataFrame([
    {
        "model": "PyTorch MLP",
        "roc_auc": roc_auc_score(y_test, probabilities),
        "average_precision": average_precision_score(y_test, probabilities),
    }
])

results.to_csv(MODEL_DIR / "baseline_metrics.csv", index=False)

print("\nBaseline metrics saved")