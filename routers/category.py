from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router = APIRouter(prefix='/categories', tags=['Categories'])

@router.post('/', response_model=schemas.CategoryOut)
def create_category(
    category: schemas.CategoryCreate,
    db : Session = Depends(get_db)
):

    if db.query(models.Category).filter(models.Category.name == category.name).first():
        raise HTTPException(status_code=400, detail="Category already exists")
    
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category

@router.get('/', response_model=list[schemas.CategoryOut])
def list_categories(db : Session = Depends(get_db)):
    return db.query(models.Category).order_by(models.Category.name).all()