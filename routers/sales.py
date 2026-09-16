from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from sqlalchemy.orm import Session
import models, schemas

router = APIRouter(prefix="/sales", tags=['Sales'])

@router.post("/", response_model = schemas.SaleOut)
def create_sale(
    sale : schemas.SaleCreate, 
    db : Session = Depends(get_db)
):
    inventory = db.query(models.Inventory).filter(models.Inventory.product_id == sale.product_id).first()

    if not inventory:
        raise HTTPException(status_code=404, detail = 'Inventory not found')

    if inventory.current_stock < sale.quantity:
        raise HTTPException(status_code=404, detauil = 'Not enough stock for this sale')

    db_sale = models.Sale(**sale.model_dump())
    db.add(db_sale)

    #sale ko stock_out movement ke roop mei bhi log krein - history complete rhegi
    db_movement = models.StockMovement(
        product_id = sale.product_id,
        movement_type = models.MovementType.stock_out,
        quantity = sale.quantity
    )

    db.add(db_movement)
    db.commit()
    db.refresh(db_sale)
    return db_sale

@router.get("/", response_model=list[schemas.SaleOut])
def list_sales(db : Session = Depends(get_db)):
    return db.query(models.Sale).all()