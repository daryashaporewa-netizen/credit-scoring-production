# Этап 1. Получение версионируемых DVC-артефактов модели
FROM python:3.12-slim AS artifacts

WORKDIR /app

RUN pip install --no-cache-dir dvc==3.67.1 dvc-gs==3.0.2

COPY .dvc ./.dvc
COPY .dvcignore dvc.yaml dvc.lock ./
COPY models/neural_network ./models/neural_network

# Без DVC_REMOTE_URL используются артефакты, заранее загруженные CI из Release.
# При наличии GCS remote DVC самостоятельно получает нужные версии модели.
ARG DVC_REMOTE_URL=""
RUN if [ -n "$DVC_REMOTE_URL" ]; then \
      dvc remote add --local --force storage "$DVC_REMOTE_URL" && \
      dvc pull \
        models/neural_network/model.onnx.dvc \
        models/neural_network/preprocessor.joblib.dvc; \
    fi && \
    test -f models/neural_network/model.onnx && \
    test -f models/neural_network/preprocessor.joblib


# Этап 2. Установка runtime-зависимостей
FROM python:3.12-slim AS builder

WORKDIR /app

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt


# Этап 3. Запуск API
FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY src ./src

COPY --from=artifacts /app/models/neural_network/model.onnx ./models/neural_network/model.onnx
COPY --from=artifacts /app/models/neural_network/preprocessor.joblib ./models/neural_network/preprocessor.joblib

RUN useradd --create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
