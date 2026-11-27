from time import perf_counter

from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field

from src.api.inference import predict_default

# Создаём FastAPI-приложение
app = FastAPI(
    title="Credit Default Prediction API",
    description="API для предсказания вероятности дефолта клиента.",
    version="1.0.0",
)

REQUESTS = Counter(
    "credit_scoring_http_requests_total",
    "Количество HTTP-запросов к API.",
    ["method", "path", "status"],
)
REQUEST_DURATION = Histogram(
    "credit_scoring_http_request_duration_seconds",
    "Продолжительность HTTP-запросов к API.",
    ["method", "path"],
)
PREDICTIONS = Counter(
    "credit_scoring_predictions_total",
    "Количество предсказаний по классам.",
    ["prediction"],
)


@app.middleware("http")
async def collect_http_metrics(request: Request, call_next):
    """Собирает количество, статусы и длительность HTTP-запросов."""

    if request.url.path == "/metrics":
        return await call_next(request)

    started_at = perf_counter()
    status = 500

    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        path = request.url.path
        REQUESTS.labels(request.method, path, str(status)).inc()
        REQUEST_DURATION.labels(request.method, path).observe(
            perf_counter() - started_at
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


@app.get("/metrics", include_in_schema=False)
def metrics():
    """Возвращает метрики приложения в формате Prometheus."""

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/predict", response_model=PredictionResponse)
def predict(data: ClientData):
    """Возвращает класс и вероятность дефолта клиента."""

    prediction, probability = predict_default(data.model_dump())
    PREDICTIONS.labels(str(prediction)).inc()

    return PredictionResponse(
        default_prediction=prediction,
        default_probability=probability,
    )
