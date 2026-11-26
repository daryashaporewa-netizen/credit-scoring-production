from fastapi import FastAPI
from pydantic import BaseModel, Field

from src.api.inference import predict_default

# Создаём FastAPI-приложение
app = FastAPI(
    title="Credit Default Prediction API",
    description="API для предсказания вероятности дефолта клиента.",
    version="1.0.0",
)


class ClientData(BaseModel):
    """Входные данные клиента."""

    LIMIT_BAL: float = Field(gt=0)

    SEX: int
    EDUCATION: int
    MARRIAGE: int
    AGE: int = Field(ge=18, le=100)

    PAY_0: int
    PAY_2: int
    PAY_3: int
    PAY_4: int
    PAY_5: int
    PAY_6: int

    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float

    PAY_AMT1: float = Field(ge=0)
    PAY_AMT2: float = Field(ge=0)
    PAY_AMT3: float = Field(ge=0)
    PAY_AMT4: float = Field(ge=0)
    PAY_AMT5: float = Field(ge=0)
    PAY_AMT6: float = Field(ge=0)


class PredictionResponse(BaseModel):
    """Ответ модели."""

    default_prediction: int
    default_probability: float


@app.get("/")
def root():
    """Проверка доступности API."""

    return {"message": "Credit Default Prediction API is running"}


@app.post("/predict", response_model=PredictionResponse)
def predict(data: ClientData):
    """Возвращает класс и вероятность дефолта клиента."""

    prediction, probability = predict_default(data.model_dump())

    return PredictionResponse(
        default_prediction=prediction,
        default_probability=probability,
    )
