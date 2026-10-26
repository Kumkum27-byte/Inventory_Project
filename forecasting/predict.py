# forecasting/predict.py
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import joblib
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException
from database import SessionLocal
import models

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demand_model.pkl")
_model = None  # loaded once, reused across requests (restart the server after retraining)


def load_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise HTTPException(
                status_code=503,
                detail="Model not trained yet. Run forecasting/train_model.py first."
            )
        _model = joblib.load(MODEL_PATH)
    return _model


def get_recent_sales(product_id, db, days=14):
    """Daily sales for the last `days` complete days (up to yesterday), zero-filled."""
    end = pd.Timestamp(datetime.now(timezone.utc).date()) - pd.Timedelta(days=1)
    idx = pd.date_range(end - pd.Timedelta(days=days - 1), end, freq="D")
    since = datetime.now(timezone.utc) - timedelta(days=days + 2)

    sales = (
        db.query(models.Sale)
        .filter(models.Sale.product_id == product_id, models.Sale.sale_date >= since)
        .all()
    )
    if sales:
        df = pd.DataFrame([{"date": s.sale_date, "quantity": s.quantity} for s in sales])
        df["date"] = pd.to_datetime(pd.to_datetime(df["date"]).dt.date)
        daily = df.groupby("date")["quantity"].sum().reindex(idx, fill_value=0)
    else:
        daily = pd.Series(0, index=idx)
    return daily.rename_axis("date").rename("quantity").reset_index()


def recursive_forecast(model, product_id, quantities, last_date, horizon_days):
    """Predict day by day, feeding each prediction back in as the next lag.
    Shared by the API and by the backtest in train_model.py, so the
    feature logic lives in exactly one place."""
    quantities = list(quantities)
    out = []
    for i in range(horizon_days):
        next_date = last_date + timedelta(days=i + 1)
        features = pd.DataFrame([{
            "product_id": product_id,
            "day_of_week": next_date.dayofweek,
            "day_of_month": next_date.day,
            "month": next_date.month,
            "lag_1": quantities[-1],
            "lag_7": quantities[-7],
            "rolling_mean_7": sum(quantities[-7:]) / 7,
        }])
        pred = max(0.0, float(model.predict(features)[0]))
        out.append((next_date, pred))
        quantities.append(pred)
    return out


def forecast_product(product_id, horizon_days=7, db=None):
    own_session = db is None
    if own_session:
        db = SessionLocal()
    try:
        if not db.query(models.Product).filter(models.Product.id == product_id).first():
            raise HTTPException(status_code=404, detail="Product not found")

        history = get_recent_sales(product_id, db)
        if history["quantity"].sum() == 0:
            raise HTTPException(
                status_code=400,
                detail="No recent sales for this product, cannot forecast"
            )
    finally:
        if own_session:
            db.close()

    model = load_model()
    result = recursive_forecast(
        model, product_id, list(history["quantity"]),
        history["date"].iloc[-1], horizon_days
    )

    forecasts = [
        {"date": str(d.date()), "predicted_quantity": round(p, 1)}
        for d, p in result
    ]
    total = sum(f["predicted_quantity"] for f in forecasts)
    return {
        "product_id": product_id,
        "horizon_days": horizon_days,
        "forecast": forecasts,
        "total_predicted_demand": round(total, 1)
    }