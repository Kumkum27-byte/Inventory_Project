# routers/forecast.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
from forecasting.predict import forecast_product

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])

ALLOWED_HORIZONS = (7, 30, 90)


@router.get("/{product_id}")
def get_forecast(
    product_id: int,
    horizon: int = Query(7, description="Days: 7, 30, or 90"),
    db: Session = Depends(get_db)
):
    if horizon not in ALLOWED_HORIZONS:
        raise HTTPException(status_code=422, detail="horizon must be 7, 30, or 90")
    return forecast_product(product_id, horizon_days=horizon, db=db)