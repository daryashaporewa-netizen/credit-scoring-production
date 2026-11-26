from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Пути к данным и результатам
ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data" / "processed"
MODEL_DIR = ROOT / "models" / "neural_network"

TARGET = "default.payment.next.month"
CATEGORICAL = ["SEX", "EDUCATION", "MARRIAGE"]

# Загружаем данные
df = pd.read_csv(DATA_DIR / "train.csv")

X = df.drop(columns=TARGET)
y = df[TARGET]

# Разделяем данные на обучение и валидацию
X_train, X_val, y_train, y_val = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

# Определяем числовые признаки
numerical = [col for col in X.columns if col not in CATEGORICAL]

# Создаём преобразователь
preprocessor = ColumnTransformer(
    transformers=[
        ("num", StandardScaler(), numerical),
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            CATEGORICAL,
        ),
    ]
)

# Обучаем преобразователь только на обучающих данных
X_train = preprocessor.fit_transform(X_train)
X_val = preprocessor.transform(X_val)

# Сохраняем преобразователь
MODEL_DIR.mkdir(parents=True, exist_ok=True)
joblib.dump(preprocessor, MODEL_DIR / "preprocessor.joblib")

print("Train:", X_train.shape)
print("Validation:", X_val.shape)
print("Preprocessor saved")
