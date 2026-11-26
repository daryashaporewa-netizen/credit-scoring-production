from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import torch
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

from src.models.neural_network.model import CreditScoringNN

# Настройки
ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models" / "neural_network"

TARGET = "default.payment.next.month"
EPOCHS = 20
BATCH_SIZE = 128
LEARNING_RATE = 0.001
RANDOM_STATE = 42

torch.manual_seed(RANDOM_STATE)
np.random.seed(RANDOM_STATE)

# Загружаем данные
df = pd.read_csv(DATA_DIR / "train.csv")

X = df.drop(columns=TARGET)
y = df[TARGET]

X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=RANDOM_STATE,
    stratify=y,
)

# Применяем сохранённую предобработку
preprocessor = joblib.load(MODEL_DIR / "preprocessor.joblib")

X_train = preprocessor.transform(X_train)
X_val = preprocessor.transform(X_val)

# Преобразуем данные в тензоры PyTorch
X_train = torch.tensor(X_train, dtype=torch.float32)
X_val = torch.tensor(X_val, dtype=torch.float32)

y_train = torch.tensor(y_train.to_numpy(), dtype=torch.float32).reshape(-1, 1)
y_val = torch.tensor(y_val.to_numpy(), dtype=torch.float32).reshape(-1, 1)

# Создаём загрузчик данных
train_dataset = TensorDataset(X_train, y_train)
train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
)

# Создаём модель
model = CreditScoringNN(input_dim=X_train.shape[1])

criterion = nn.BCEWithLogitsLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

best_auc = 0.0

# Обучение
for epoch in range(EPOCHS):
    model.train()
    total_loss = 0.0

    for X_batch, y_batch in train_loader:
        optimizer.zero_grad()

        logits = model(X_batch)
        loss = criterion(logits, y_batch)

        loss.backward()
        optimizer.step()

        total_loss += loss.item() * len(X_batch)

    train_loss = total_loss / len(train_dataset)

    # Оценка на валидационной выборке
    model.eval()

    with torch.no_grad():
        val_logits = model(X_val)
        val_probs = torch.sigmoid(val_logits).numpy().ravel()

    val_auc = roc_auc_score(y_val.numpy().ravel(), val_probs)

    print(
        f"Epoch {epoch + 1:02d}/{EPOCHS} | "
        f"Loss: {train_loss:.4f} | "
        f"Val ROC-AUC: {val_auc:.4f}"
    )

    # Сохраняем лучшую модель
    if val_auc > best_auc:
        best_auc = val_auc
        torch.save(model.state_dict(), MODEL_DIR / "best_model.pth")

print(f"\nBest validation ROC-AUC: {best_auc:.4f}")
print("Model saved:", MODEL_DIR / "best_model.pth")
