from pathlib import Path
from time import perf_counter

import numpy as np
import onnxruntime as ort
import pandas as pd
import torch

from src.models.neural_network.model import CreditScoringNN

# Настройки эксперимента
ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = ROOT / "models" / "neural_network"

BATCH_SIZES = [1, 32, 128]
WARMUP = 20
REPEATS = 100
INPUT_DIM = 37

# Используем один поток CPU для обеих моделей
torch.set_num_threads(1)

# Загружаем PyTorch-модель
model = CreditScoringNN(input_dim=INPUT_DIM)
model.load_state_dict(
    torch.load(
        MODEL_DIR / "best_model.pth",
        map_location="cpu",
        weights_only=True,
    )
)
model.eval()

# Загружаем ONNX-модель
options = ort.SessionOptions()
options.intra_op_num_threads = 1
options.inter_op_num_threads = 1

session = ort.InferenceSession(
    str(MODEL_DIR / "model.onnx"),
    sess_options=options,
    providers=["CPUExecutionProvider"],
)


def measure(inference_fn):
    # Прогреваем модель
    for _ in range(WARMUP):
        inference_fn()

    times = []

    # Измеряем время инференса
    for _ in range(REPEATS):
        start = perf_counter()
        inference_fn()
        times.append(perf_counter() - start)

    return np.array(times)


results = []

for batch_size in BATCH_SIZES:
    # Одинаковые входные данные для обеих моделей
    X = (
        np.random.default_rng(42)
        .normal(size=(batch_size, INPUT_DIM))
        .astype(np.float32)
    )

    X_torch = torch.from_numpy(X)

    def pytorch_inference():
        with torch.inference_mode():
            return model(X_torch)

    def onnx_inference():
        return session.run(None, {"input": X})

    for name, inference_fn in [
        ("PyTorch", pytorch_inference),
        ("ONNX Runtime", onnx_inference),
    ]:
        times = measure(inference_fn)

        latency_ms = times.mean() * 1000
        p95_ms = np.percentile(times, 95) * 1000
        throughput = batch_size / times.mean()

        results.append((name, batch_size, latency_ms, p95_ms, throughput))

# Выводим результаты
print(
    f"{'Model':<15} {'Batch':>6} " f"{'Mean ms':>12} {'P95 ms':>12} {'Samples/s':>12}"
)

for name, batch, latency, p95, throughput in results:
    print(
        f"{name:<15} {batch:>6} "
        f"{latency:>12.4f} {p95:>12.4f} "
        f"{throughput:>12.1f}"
    )


# Сохраняем результаты benchmark
benchmark_df = pd.DataFrame(
    results,
    columns=[
        "model",
        "batch_size",
        "mean_latency_ms",
        "p95_latency_ms",
        "throughput_samples_per_sec",
    ],
)

benchmark_df.to_csv(
    MODEL_DIR / "benchmark_results.csv",
    index=False,
)

print("\nBenchmark results saved")
