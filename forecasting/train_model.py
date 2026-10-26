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
from forecasting.predict import MODEL_PATH, recursive_forecast

FEATURE_COLS = ["product_id", "day_of_week", "day_of_month", "month",
                "lag_1", "lag_7", "rolling_mean_7"]
PARAMS = dict(n_estimators=200, max_depth=4, learning_rate=0.05, random_state=42)
TEST_DAYS = 14          # last 14 days of every product are held out
BACKTEST_HORIZON = 7    # multi-day backtest length


def load_sales_data():
    db = SessionLocal()
    try:
        sales = db.query(models.Sale).all()
    finally:
        db.close()
    if not sales:
        raise SystemExit("No sales data found. Run seed_data.py first.")

    df = pd.DataFrame([
        {"product_id": s.product_id, "quantity": s.quantity, "sale_date": s.sale_date}
        for s in sales
    ])
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    return df


def build_features(df):
    # daily sales per product, missing days = 0 sale
    df["date"] = df["sale_date"].dt.date
    daily = df.groupby(["product_id", "date"])["quantity"].sum().reset_index()

    all_rows = []
    for pid in daily["product_id"].unique():
        pdf = daily[daily["product_id"] == pid].copy()
        pdf["date"] = pd.to_datetime(pdf["date"])
        pdf = pdf.set_index("date").asfreq("D", fill_value=0).reset_index()
        pdf["product_id"] = pid

        pdf["day_of_week"] = pdf["date"].dt.dayofweek
        pdf["day_of_month"] = pdf["date"].dt.day
        pdf["month"] = pdf["date"].dt.month

        pdf["lag_1"] = pdf["quantity"].shift(1)
        pdf["lag_7"] = pdf["quantity"].shift(7)
        pdf["rolling_mean_7"] = pdf["quantity"].shift(1).rolling(7).mean()

        all_rows.append(pdf)

    return pd.concat(all_rows).dropna().reset_index(drop=True)


def train():
    data = build_features(load_sales_data())

    # time-based split: same cutoff date for every product
    cutoff = data["date"].max() - pd.Timedelta(days=TEST_DAYS)
    train_df = data[data["date"] <= cutoff]
    test_df = data[data["date"] > cutoff]

    model = xgb.XGBRegressor(**PARAMS)
    model.fit(train_df[FEATURE_COLS], train_df["quantity"])

    # 1) one-day-ahead error (uses real lags) vs a naive baseline
    X_test, y_test = test_df[FEATURE_COLS], test_df["quantity"]
    preds = model.predict(X_test)
    mae = mean_absolute_error(y_test, preds)
    rmse = np.sqrt(mean_squared_error(y_test, preds))
    base_mae = mean_absolute_error(y_test, X_test["rolling_mean_7"])
    print(f"[1-day ahead]  model MAE {mae:.2f} | RMSE {rmse:.2f} | "
          f"baseline (7-day avg) MAE {base_mae:.2f}")

    # 2) honest multi-day backtest: recursive forecast, like the API does
    model_errs, base_errs = [], []
    for pid in data["product_id"].unique():
        hist = train_df[train_df["product_id"] == pid].sort_values("date")
        actual = test_df[test_df["product_id"] == pid].sort_values("date").head(BACKTEST_HORIZON)
        if len(hist) < 7 or len(actual) < BACKTEST_HORIZON:
            continue
        qs = list(hist["quantity"])
        fc = recursive_forecast(model, pid, qs, hist["date"].iloc[-1], BACKTEST_HORIZON)
        pred = np.array([p for _, p in fc])
        truth = actual["quantity"].values
        model_errs += list(np.abs(pred - truth))
        base_errs += list(np.abs(np.mean(qs[-7:]) - truth))

    if model_errs:
        print(f"[{BACKTEST_HORIZON}-day recursive] model MAE {np.mean(model_errs):.2f} | "
              f"baseline MAE {np.mean(base_errs):.2f}")

    # final model: refit on ALL data after evaluation, then save
    final_model = xgb.XGBRegressor(**PARAMS)
    final_model.fit(data[FEATURE_COLS], data["quantity"])
    joblib.dump(final_model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")


if __name__ == "__main__":
    train()