import models
from forecasting.predict import forecast_product
from sqlalchemy import func
from datetime import datetime, timedelta

def get_low_stock_products(db):
    results = (
        db.query(models.Inventory, models.Product)
        .join(models.Product, models.Inventory.product_id == models.Product.id)
        .filter(models.Inventory.current_stock <= models.Product.reorder_level)
        .all()
    )

    return[
        {
            "product_id" : p.id,
            "product_name" : p.name,
            "current_stock" : inv.current_stock,
            "reorder_level" : p.reorder_level
        }
        for inv, p in results
    ]

def get_forecast_summary(product_id, horizon_days=7):
    return forecast_product (product_id, horizon_days=horizon_days)

def get_slow_moving_products(db, days=30, threshold=5):
    cutoff_date = datetime.now() - timedelta(days=days)
    results = (
        db.query(models.Product, func.coalesce(func.sum(models.Sale.quantity),0).label("total_sold"))
        .outerjoin(models.Sale, models.Sale.product_id == models.Product.id)
        .filter(models.Sale.sale_date >= cutoff_date)
        .group_by(models.Product.id)
        .having(func.coalesce(func.sum(models.Sale.quantity),0) < threshold)
        .all()
    )

    return[
        {
            "product_id" : p.id,
            "product_name" : p.name,
            "total_sold_last_30_days" : int(total)
        }
        for p, total in results
    ]