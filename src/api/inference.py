from pathlib import Path

import joblib
import numpy as np
import onnxruntime as ort
import pandas as pd

from src.features.build_features import build_features

# Пути к артефактам нейронной сети
ROOT = Path(__file__).resolve().parents[2]
MODEL_DIR = ROOT / "models" / "neural_network"

# Загружаем сохранённую предобработку
preprocessor = joblib.load(MODEL_DIR / "preprocessor.joblib")

# Загружаем ONNX-модель
session = ort.InferenceSession(
    str(MODEL_DIR / "model.onnx"),
    providers=["CPUExecutionProvider"],
)


def predict_default(data: dict):
    # Преобразуем данные клиента в DataFrame
    df = pd.DataFrame([data])

    # Создаём дополнительные признаки
    df = build_features(df)

    # Применяем сохранённую предобработку
    X = preprocessor.transform(df).astype(np.float32)

    # Получаем логит ONNX-модели
    logits = session.run(None, {"input": X})[0]

    # Преобразуем логит в вероятность дефолта
    probability = float(1 / (1 + np.exp(-logits[0, 0])))

    # Определяем предсказанный класс
    prediction = int(probability >= 0.5)

    return prediction, probability
