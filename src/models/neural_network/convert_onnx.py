from pathlib import Path

import onnx
import torch

from src.models.neural_network.model import CreditScoringNN

# Пути к файлам модели
ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = ROOT / "models" / "neural_network"

# Загружаем обученную нейронную сеть
model = CreditScoringNN(input_dim=37)

model.load_state_dict(
    torch.load(
        MODEL_DIR / "best_model.pth",
        map_location="cpu",
        weights_only=True,
    )
)

model.eval()

# Пример входных данных для экспорта
dummy_input = torch.randn(1, 37)

# Конвертируем модель в ONNX
onnx_path = MODEL_DIR / "model.onnx"

torch.onnx.export(
    model,
    dummy_input,
    str(onnx_path),
    input_names=["input"],
    output_names=["logits"],
    dynamic_axes={
        "input": {0: "batch_size"},
        "logits": {0: "batch_size"},
    },
    opset_version=17,
    dynamo=False,
)

# Проверяем корректность структуры ONNX
onnx_model = onnx.load(str(onnx_path))
onnx.checker.check_model(onnx_model)

print("ONNX model saved:", onnx_path)
print("ONNX model validation passed")
