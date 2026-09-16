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
    db_category = models.Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category