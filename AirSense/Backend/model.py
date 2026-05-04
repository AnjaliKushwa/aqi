import pandas as pd
from preprocess import load_data, split_features_target
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error
from xgboost import XGBRegressor
import joblib

# Load data
df = load_data()

#  FEATURE ENGINEERING (MUST MATCH API)
df["pm_ratio"] = df["pm25"] / (df["pm10"] + 1)
df["pm_avg"] = (df["pm25"] + df["pm10"]) / 2
df["gas_avg"] = (df["no2"] + df["so2"] + df["o3"]) / 3
df["gas_total"] = df["no2"] + df["so2"] + df["o3"]

# Split features
X, y = split_features_target(df)

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

#  IMPROVED MODEL
model = XGBRegressor(
    n_estimators=500,
    learning_rate=0.03,
    max_depth=8,
    subsample=0.8,
    colsample_bytree=0.8
)

# Train
model.fit(X_train, y_train)

# Predict
y_pred = model.predict(X_test)

# Evaluation
print("R2 Score:", r2_score(y_test, y_pred))
print("MAE:", mean_absolute_error(y_test, y_pred))

# Save model
joblib.dump(model, "model.pkl")

print("✅ Model trained successfully!")