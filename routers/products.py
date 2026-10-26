from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix='/products', tags=['Products'])


@router.post('/', response_model=schemas.ProductOut)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):
    if db.query(models.Product).filter(models.Product.sku == product.sku).first():
        raise HTTPException(status_code=400, detail='SKU already exists')

    if not db.query(models.Category).filter(models.Category.id == product.category_id).first():
        raise HTTPException(status_code=404, detail='Category not found')
    if product.supplier_id is not None and not db.query(models.Supplier).filter(
        models.Supplier.id == product.supplier_id
    ).first():
        raise HTTPException(status_code=404, detail='Supplier not found')

    # initial_stock is not a Product column, it goes into Inventory below
    db_product = models.Product(**product.model_dump(exclude={"initial_stock"}))
    db.add(db_product)
    db.flush()  # assigns db_product.id without committing

    # inventory row + (if any stock) a stock_in movement, so ledger and stock agree
    db.add(models.Inventory(product_id=db_product.id, current_stock=product.initial_stock))
    if product.initial_stock > 0:
        db.add(models.StockMovement(
            product_id=db_product.id,
            movement_type=models.MovementType.stock_in,
            quantity=product.initial_stock
        ))

    db.commit()
    db.refresh(db_product)
    return db_product


@router.get('/', response_model=list[schemas.ProductOut])
def list_products(db: Session = Depends(get_db)):
    return db.query(models.Product).all()


@router.get('/{product_id}', response_model=schemas.ProductOut)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return product