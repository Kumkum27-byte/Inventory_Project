from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone, time
from database import get_db
import models, schemas

router = APIRouter(prefix="/sales", tags=['Sales'])

IST = timezone(timedelta(hours=5, minutes=30))


@router.post("/", response_model=schemas.SaleOut)
def create_sale(
    sale: schemas.SaleCreate,
    db: Session = Depends(get_db)
):
    inventory = (
        db.query(models.Inventory)
        .filter(models.Inventory.product_id == sale.product_id)
        .with_for_update()
        .first()
    )
    if not inventory:
        raise HTTPException(status_code=404, detail='Inventory not found')

    if inventory.current_stock < sale.quantity:
        raise HTTPException(status_code=400, detail='Not enough stock for this sale')

    inventory.current_stock -= sale.quantity

    db_sale = models.Sale(**sale.model_dump())
    db.add(db_sale)

    # log the sale as a stock_out movement so history stays complete
    db.add(models.StockMovement(
        product_id=sale.product_id,
        movement_type=models.MovementType.stock_out,
        quantity=sale.quantity
    ))

    db.commit()
    db.refresh(db_sale)
    return db_sale


@router.get("/", response_model=list[schemas.SaleOut])
def list_sales(db: Session = Depends(get_db)):
    return db.query(models.Sale).all()


@router.get("/daily/{product_id}")
def daily_sales(
    product_id: int,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Units sold per day for one product (for the history line in the chart)."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    day = func.date(models.Sale.sale_date)
    rows = (
        db.query(day.label("date"), func.sum(models.Sale.quantity).label("quantity"))
        .filter(models.Sale.product_id == product_id, models.Sale.sale_date >= since)
        .group_by(day)
        .order_by(day)
        .all()
    )
    return [{"date": str(r.date), "quantity": int(r.quantity)} for r in rows]

@router.get("/daily")
def daily_sales_all(
    days : int = Query(30, ge=1, le=365),
    db : Session = Depends(get_db)
):

    """Units sold per day across ALL products, one row per day (zeros included).
    Days are cut at midnight India time, not midnight UTC."""

    first = datetime.now(IST).date() - timedelta(days=days-1)
    start = datetime.combine(first, time.min, tzinfo=IST)
    day = func.date(func.timezone("Asia/Kolkata", models.Sale.sale_date))

    rows = (
        db.query(day.label("date"), func.sum(models.Sale.quantity).label("units"))
        .filter(models.Sale.sale_date >= start)
        .group_by(day)
        .all()
    )
    by_day = {str(r.date): int(r.units) for r in rows}

    out = []
    for i in range(days):
        d = str(first + timedelta(days=i))
        out.append({"date" : d, "units" : by_day.get(d, 0)})
    return out


@router.get("/top-products")
def top_products(
    days : int = Query(30, ge=1, le=365),
    limit : int = Query(5, ge=1, le=20),
    db : Session = Depends(get_db)
):
    """Best sellers (by units) over the last 'days' days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)
    total = func.sum(models.Sale.quantity)
    rows = (
        db.query(models.product.id, models.Product,name, models.Product.image_url, total.label("units"))
        .join(models.Sale, models.Sale.product_id == models.Product.id)
        .filter(models.Sale.sale_date >= since)
        .group_by(models.Product.id)
        .order_by(total.desc())
        .limit(limit)
        .all()
    )

    return [
        {"product_id" : r.id,
         "name" : r.name,
         "image_url" : r.iamge_url,
         "units" : int(r.units)
        }
        for r in rows
    ]