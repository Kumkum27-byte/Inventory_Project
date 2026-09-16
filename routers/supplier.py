from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas

router =  APIRouter(prefix='/suppliers', tags=['Suppliers1'])

@router.post('/', response_model=schemas.SupplierOut)
def create_supplier(
    supplier : schemas.SupplierCreate, 
    db : Session = Depends(get_db)
):
    db_supplier = models.Supplier(**supplier.model_dump())
    db.add(db_supplier)
    db.commit()
    db.refersh(db_supplier)
    return db_supplier

@router.get('/', response_model = list[schemas.SupplierOut])
def list_suppliers(db : Session = Depends(get_db)):
    return db.query(models.Supplier).all()