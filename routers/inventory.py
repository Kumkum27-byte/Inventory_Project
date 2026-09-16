from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
import schemas, models

router = APIRouter(prefix='/inventory', tags = ['inventory'])

@router.post('/stock_movement', response_model = schemas.StockMovementOut)
def create_stock_movement(
    movement : schemas.StockMovementCreate, 
    db : Session = Depends(get_db)
):
    inventory  = db.query(models.Inventory).filter(models.Inventory.product_id == movement.product_id).first()

    if not inventory:
        raise HTTPException(status_code = 404, detail = 'Inventory not found')

    if movement.movement_type == movement.MovementType.stock_out and inventory.current_stock < movement.quantity:
        raise HTTPException(status_code = 404, detail = 'Not enough stock to fulfill stock_out request')

    #Stept-1: movement history record
    db_movement = models.StockMovement(**movement.model_dump())
    db.add(db_movement)

    #Step-2: Current_Stock update - same transaction, thass why out of sync nii hoga
    if movement.movement_type == models.MovementType.stock_in:
        inventory.current_stock += movement.quantity

    else:
        inventory.current_stock -= movement.quantity

    db.commit()
    db.refresh(db_movement)
    return db_movement

@router.get("/", response_model=list[schemas.InventoryOut])
def list_inventory(db: Session = Depends(get_db)):
    return db.query(models.Inventory).all()