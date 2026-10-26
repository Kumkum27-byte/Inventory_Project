from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
import schemas, models
from assistant.data_retrieval import get_low_stock_products
from forecasting.predict import forecast_product

router = APIRouter(prefix='/inventory', tags=['inventory'])


def get_locked_inventory(db: Session, product_id: int) -> models.Inventory:
    """Fetch the inventory row with a row lock so concurrent requests
    for the same product wait for each other (prevents lost updates)."""
    inventory = (
        db.query(models.Inventory)
        .filter(models.Inventory.product_id == product_id)
        .with_for_update()
        .first()
    )
    if not inventory:
        raise HTTPException(status_code=404, detail='Inventory not found')
    return inventory


@router.post('/stock-movement', response_model=schemas.StockMovementOut)
def create_stock_movement(
    movement: schemas.StockMovementCreate,
    db: Session = Depends(get_db)
):
    inventory = get_locked_inventory(db, movement.product_id)

    if movement.movement_type == models.MovementType.stock_out:
        if inventory.current_stock < movement.quantity:
            raise HTTPException(
                status_code=400,
                detail='Not enough stock to fulfill stock_out request'
            )
        inventory.current_stock -= movement.quantity
    else:
        inventory.current_stock += movement.quantity

    db_movement = models.StockMovement(**movement.model_dump())
    db.add(db_movement)

    # one commit: movement record + stock update succeed or fail together
    db.commit()
    db.refresh(db_movement)
    return db_movement


@router.get("/", response_model=list[schemas.InventoryOut])
def list_inventory(db: Session = Depends(get_db)):
    return db.query(models.Inventory).all()


@router.get("/low-stock")
def low_stock(db: Session = Depends(get_db)):
    # same function the copilot uses, so dashboard and copilot never disagree
    return get_low_stock_products(db)


@router.get("/catalog", response_model=list[schemas.Catalogitem])
def catalog(category_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Everything one product card needs in a single call.
    Optional ?category_id= filters to one category."""
    query = (
        db.query(models.Product, models.Category, models.Inventory)
        .outerjoin(models.Category, models.Product.category_id == models.Category.id)
        .outerjoin(models.Inventory, models.Inventory.product_id == models.Product.id)
    )
    if category_id is not None:
        query = query.filter(models.Product.category_id == category_id)

    return [
        {
            "id": p.id,
            "name": p.name,
            "sku": p.sku,
            "image_url": p.image_url,
            "unit_price": p.unit_price,
            "reorder_level": p.reorder_level,
            "category_id": p.category_id,
            "category_name": c.name if c else None,
            "current_stock": inv.current_stock if inv else 0,
        }
        for p, c, inv in query.order_by(models.Product.name).all()
    ]


@router.get("/reorder-plan")
def reorder_plan(
    horizon: int = Query(7, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Every low-stock product with how many units to order.
    suggested = predicted demand + reorder level - units left.
    If the ML forecast is not possible (no recent sales / no model), falls back
    to a simple rule (top up to 2x the reorder level) and says so in `source`."""
    rows = (
        db.query(models.Product, models.Category, models.Inventory)
        .join(models.Inventory, models.Inventory.product_id == models.Product.id)
        .outerjoin(models.Category, models.Product.category_id == models.Category.id)
        .filter(models.Inventory.current_stock <= models.Product.reorder_level)
        .order_by(models.Inventory.current_stock.asc())
        .all()
    )

    plan = []
    for p, c, inv in rows:
        try:
            fc = forecast_product(p.id, horizon_days=horizon, db=db)
            demand = float(fc["total_predicted_demand"])
            suggested = max(0, round(demand + p.reorder_level - inv.current_stock))
            source = "forecast"
        except HTTPException:
            demand = None
            suggested = max(0, p.reorder_level * 2 - inv.current_stock)
            source = "rule"

        plan.append({
            "product_id": p.id,
            "name": p.name,
            "category_name": c.name if c else None,
            "current_stock": inv.current_stock,
            "reorder_level": p.reorder_level,
            "predicted_demand": None if demand is None else round(demand, 1),
            "suggested_order_qty": int(suggested),
            "source": source,
        })
    return plan