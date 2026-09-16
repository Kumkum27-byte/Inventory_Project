# forecasting/predict.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import joblib
from datetime import timedelta
from database import SessionLocal
import models

MODEL_PATH = os.path.join(os.path.dirname(__file__), "demand_model.pkl")

def get_recent_sales(product_id, db, days=14):
    sales = (
        db.query(models.Sale)
        .filter(models.Sale.product_id == product_id)
        .order_by(models.Sale.sale_date.desc())
        .limit(days)
        .all()
    )
    data = [{"date": s.sale_date, "quantity": s.quantity} for s in sales]
    df = pd.DataFrame(data)
    if df.empty:
        return df
    df["date"] = pd.to_datetime(df["date"]).dt.date
    daily = df.groupby("date")["quantity"].sum().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.set_index("date").asfreq("D", fill_value=0).reset_index()
    return daily

def forecast_product(product_id, horizon_days=7):
    model = joblib.load(MODEL_PATH)
    db = SessionLocal()
    history = get_recent_sales(product_id, db)
    db.close()

    if history.empty or len(history) < 7:
        return {"error": "Not enough sales history for this product"}

    history = history.sort_values("date").reset_index(drop=True)
    quantities = list(history["quantity"])
    last_date = history["date"].iloc[-1]

    forecasts = []
    for i in range(horizon_days):
        next_date = last_date + timedelta(days=i + 1)
        lag_1 = quantities[-1]
        lag_7 = quantities[-7] if len(quantities) >= 7 else quantities[0]
        rolling_mean_7 = sum(quantities[-7:]) / min(len(quantities), 7)

        features = pd.DataFrame([{
            "product_id": product_id,
            "day_of_week": next_date.dayofweek,
            "day_of_month": next_date.day,
            "month": next_date.month,
            "lag_1": lag_1,
            "lag_7": lag_7,
            "rolling_mean_7": rolling_mean_7
        }])

        pred = max(0, round(float(model.predict(features)[0]), 1))
        forecasts.append({"date": str(next_date.date()), "predicted_quantity": pred})
        quantities.append(pred)

    total = sum(f["predicted_quantity"] for f in forecasts)
    return {
        "product_id": product_id,
        "horizon_days": horizon_days,
        "forecast": forecasts,
        "total_predicted_demand": round(total, 1)
    }