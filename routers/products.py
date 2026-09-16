from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix='/products', tags=['Products'])

@router.post('/', response_model=schemas.ProductOut)
def create_product(
    product : schemas.ProductCreate,
    db : Session = Depends(get_db)
):
    existing = db.query(models.Product).filter(models.Product.sku == product.sku).first()
    if existing : 
        raise HTTPException(status_code=400, detail = 'SKU already exists')

    db_product = models.Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

    #product ke saath inventory row making
    db_inventory = models.Inventory(product_id = db_product.id, current_stock=0)
    db.add(db_inventory)
    db.commit()
    
    return db_inventory

@router.get('/', response_model = list[schemas.ProductOut])
def list_products(db : Session = Depends(get_db)):
    return db.query(models.Product).all()

@router.get('/{product_id}', response_model = schemas.ProductOut)
def get_product(
    product_id : int,
    db : Session = Depends(get_db)
):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail='Product not found')
    return product