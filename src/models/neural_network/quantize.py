from pathlib import Path

import onnx
from onnxruntime.quantization import QuantType, quantize_dynamic

# Пути к моделям
ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = ROOT / "models" / "neural_network"

original_path = MODEL_DIR / "model.onnx"
quantized_path = MODEL_DIR / "model_int8.onnx"

# Выполняем динамическое INT8-квантование
quantize_dynamic(
    model_input=str(original_path),
    model_output=str(quantized_path),
    weight_type=QuantType.QInt8,
)

# Проверяем структуру оптимизированной модели
model = onnx.load(str(quantized_path))
onnx.checker.check_model(model)

# Сравниваем размеры файлов
original_size = original_path.stat().st_size
quantized_size = quantized_path.stat().st_size

reduction = (1 - quantized_size / original_size) * 100

print(f"Original ONNX: {original_size / 1024:.2f} KB")
print(f"Quantized ONNX: {quantized_size / 1024:.2f} KB")
print(f"Size reduction: {reduction:.2f}%")
print("Quantized model validation passed")
