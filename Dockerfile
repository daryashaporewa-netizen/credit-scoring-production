# Этап 1. Установка зависимостей
FROM python:3.12-slim AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt


# Этап 2. Запуск API
FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY src ./src

COPY models/neural_network/model.onnx ./models/neural_network/model.onnx
COPY models/neural_network/preprocessor.joblib ./models/neural_network/preprocessor.joblib

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]