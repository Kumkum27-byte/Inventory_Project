import models
from forecasting.predict import forecast_product
from sqlalchemy import func, and_
from datetime import datetime, timedelta, timezone


def get_low_stock_products(db):
    results = (
        db.query(models.Inventory, models.Product)
        .join(models.Product, models.Inventory.product_id == models.Product.id)
        .filter(models.Inventory.current_stock <= models.Product.reorder_level)
        .all()
    )

    return [
        {
            "product_id": p.id,
            "product_name": p.name,
            "current_stock": inv.current_stock,
            "reorder_level": p.reorder_level
        }
        for inv, p in results
    ]


def get_forecast_summary(product_id, horizon_days=7):
    return forecast_product(product_id, horizon_days=horizon_days)


def get_slow_moving_products(db, days=30, limit=3):
    """The `limit` slowest sellers over the last `days` days.
    The date condition is in the JOIN's ON clause (not WHERE), so products
    with zero sales in the period are kept, with a total of 0."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    total_sold = func.coalesce(func.sum(models.Sale.quantity), 0)

    results = (
        db.query(models.Product, total_sold.label("total_sold"))
        .outerjoin(
            models.Sale,
            and_(
                models.Sale.product_id == models.Product.id,
                models.Sale.sale_date >= cutoff
            )
        )
        .group_by(models.Product.id)
        .order_by(total_sold.asc())
        .limit(limit)
        .all()
    )

    return [
        {
            "product_id": p.id,
            "product_name": p.name,
            "units_sold": int(total),
            "period_days": days
        }
        for p, total in results
    ]