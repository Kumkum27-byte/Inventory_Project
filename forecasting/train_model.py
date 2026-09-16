# forecasting/train_model.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
from database import SessionLocal
import models

def load_sales_data():
    db = SessionLocal()
    sales = db.query(models.Sale).all()
    db.close()

    data = [{"product_id": s.product_id, "quantity": s.quantity, "sale_date": s.sale_date} for s in sales]
    df = pd.DataFrame(data)
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    return df

def build_features(df):
    # daily sales per product — missing days = 0 sale
    df["date"] = df["sale_date"].dt.date
    daily = df.groupby(["product_id", "date"])["quantity"].sum().reset_index()

    all_rows = []
    for pid in daily["product_id"].unique():
        pdf = daily[daily["product_id"] == pid].copy()
        pdf["date"] = pd.to_datetime(pdf["date"])
        pdf = pdf.set_index("date").asfreq("D", fill_value=0).reset_index()
        pdf["product_id"] = pid

        # calendar features
        pdf["day_of_week"] = pdf["date"].dt.dayofweek
        pdf["day_of_month"] = pdf["date"].dt.day
        pdf["month"] = pdf["date"].dt.month

        # lag features
        pdf["lag_1"] = pdf["quantity"].shift(1)
        pdf["lag_7"] = pdf["quantity"].shift(7)
        pdf["rolling_mean_7"] = pdf["quantity"].shift(1).rolling(7).mean()

        all_rows.append(pdf)

    result = pd.concat(all_rows).dropna()
    return result

def train():
    df = load_sales_data()
    features_df = build_features(df)

    feature_cols = ["product_id", "day_of_week", "day_of_month", "month", "lag_1", "lag_7", "rolling_mean_7"]
    X = features_df[feature_cols]
    y = features_df["quantity"]

    split_idx = int(len(X) * 0.85)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]

    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        random_state=42
    )
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    print(f"MAE: {mae:.2f}, RMSE: {rmse:.2f}")

    joblib.dump(model, "forecasting/demand_model.pkl")
    print("Model saved to forecasting/demand_model.pkl")

if __name__ == "__main__":
    train()