from pathlib import Path
from time import perf_counter

import numpy as np
import pandas as pd
import torch

from src.models.neural_network.model import CreditScoringNN

ROOT = Path(__file__).resolve().parents[3]
MODEL_DIR = ROOT / "models" / "neural_network"

BATCH_SIZES = [1, 32, 128]
WARMUP = 50
REPEATS = 200
INPUT_DIM = 37

torch.set_num_threads(1)

# Загружаем обученные веса
weights = torch.load(
    MODEL_DIR / "best_model.pth",
    map_location="cpu",
    weights_only=True,
)


def measure(model, X, device):
    # Прогрев
    with torch.inference_mode():
        for _ in range(WARMUP):
            model(X)

        if device.type == "mps":
            torch.mps.synchronize()

        times = []

        for _ in range(REPEATS):
            start = perf_counter()

            model(X)

            if device.type == "mps":
                torch.mps.synchronize()

            times.append(perf_counter() - start)

    return np.array(times)


results = []

for device_name in ["cpu", "mps"]:
    device = torch.device(device_name)

    model = CreditScoringNN(input_dim=INPUT_DIM)
    model.load_state_dict(weights)
    model = model.to(device)
    model.eval()

    for batch_size in BATCH_SIZES:
        # Одинаковые данные для CPU и GPU
        rng = np.random.default_rng(42)
        X_numpy = rng.normal(size=(batch_size, INPUT_DIM)).astype(np.float32)

        X = torch.from_numpy(X_numpy).to(device)

        times = measure(model, X, device)

        mean_ms = times.mean() * 1000
        p95_ms = np.percentile(times, 95) * 1000
        throughput = batch_size / times.mean()

        results.append((device_name, batch_size, mean_ms, p95_ms, throughput))

# Формируем таблицу результатов
df = pd.DataFrame(
    results,
    columns=[
        "device",
        "batch_size",
        "mean_latency_ms",
        "p95_latency_ms",
        "throughput_samples_per_sec",
    ],
)

print(df.round(4).to_string(index=False))

# Сохраняем результаты
df.to_csv(MODEL_DIR / "benchmark_gpu_results.csv", index=False)

print("\nCPU/GPU benchmark results saved")
