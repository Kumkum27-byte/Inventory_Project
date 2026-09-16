# routers/forecast.py
from fastapi import APIRouter, Query
from forecasting.predict import forecast_product

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])

@router.get("/{product_id}")
def get_forecast(product_id: int, horizon: int = Query(7, description="Days: 7, 30, or 90")):
    return forecast_product(product_id, horizon_days=horizon)