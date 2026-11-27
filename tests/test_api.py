import sys
from types import ModuleType
from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

# Подменяем модуль инференса, чтобы не загружать ONNX-модель
mock_inference = ModuleType("src.api.inference")
mock_inference.predict_default = Mock(return_value=(1, 0.5789))

with patch.dict(sys.modules, {"src.api.inference": mock_inference}):
    from src.api.app import app

client = TestClient(app)


def test_predict():
    data = {
        "LIMIT_BAL": 20000,
        "SEX": 2,
        "EDUCATION": 2,
        "MARRIAGE": 1,
        "AGE": 24,
        "PAY_0": 2,
        "PAY_2": 2,
        "PAY_3": -1,
        "PAY_4": -1,
        "PAY_5": -2,
        "PAY_6": -2,
        "BILL_AMT1": 3913,
        "BILL_AMT2": 3102,
        "BILL_AMT3": 689,
        "BILL_AMT4": 0,
        "BILL_AMT5": 0,
        "BILL_AMT6": 0,
        "PAY_AMT1": 0,
        "PAY_AMT2": 689,
        "PAY_AMT3": 0,
        "PAY_AMT4": 0,
        "PAY_AMT5": 0,
        "PAY_AMT6": 0,
    }

    response = client.post("/predict", json=data)

    assert response.status_code == 200
    assert response.json()["default_prediction"] == 1
    assert response.json()["default_probability"] == 0.5789


def test_metrics():
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "credit_scoring_http_requests_total" in response.text
    assert "credit_scoring_predictions_total" in response.text
