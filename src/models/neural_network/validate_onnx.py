from pathlib import Path

import joblib
import numpy as np
import onnxruntime as ort
import pandas as pd
import torch

from src.models.neural_network.model import CreditScoringNN


# Пути к данным и моделям
ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = ROOT / "models" / "neural_network"
DATA_PATH = ROOT / "data" / "processed" / "test.csv"

TARGET = "default.payment.next.month"

# Загружаем тестовые данные
df = pd.read_csv(DATA_PATH)
X_test = df.drop(columns=TARGET)

# Применяем сохранённую предобработку
preprocessor = joblib.load(MODEL_DIR / "preprocessor.joblib")
X_test = preprocessor.transform(X_test).astype(np.float32)

# Предсказания PyTorch
model = CreditScoringNN(input_dim=X_test.shape[1])
model.load_state_dict(
    torch.load(
        MODEL_DIR / "best_model.pth",
        map_location="cpu",
        weights_only=True,
    )
)
model.eval()

with torch.no_grad():
    torch_logits = model(torch.from_numpy(X_test)).numpy()

# Предсказания ONNX Runtime
session = ort.InferenceSession(
    str(MODEL_DIR / "model.onnx"),
    providers=["CPUExecutionProvider"],
)

onnx_logits = session.run(
    ["logits"],
    {"input": X_test},
)[0]

# Сравниваем выходы моделей
torch_probs = torch.sigmoid(torch.from_numpy(torch_logits)).numpy()
onnx_probs = 1 / (1 + np.exp(-onnx_logits))

difference = np.abs(torch_probs - onnx_probs)

print("Max absolute difference:", difference.max())
print("Mean absolute difference:", difference.mean())

# Проверяем численную близость
np.testing.assert_allclose(
    torch_probs,
    onnx_probs,
    rtol=1e-5,
    atol=1e-6,
)

# Проверяем совпадение классов
torch_classes = (torch_probs >= 0.5).astype(int)
onnx_classes = (onnx_probs >= 0.5).astype(int)

agreement = np.mean(torch_classes == onnx_classes)

print(f"Class agreement: {agreement:.2%}")
print("ONNX validation passed")