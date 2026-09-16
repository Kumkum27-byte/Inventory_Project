from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models import MovementType

class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class CategoryOut(CategoryBase):
    id : int
    class config:
        from_attributes = True

class SupplierBase(BaseModel):
    name : str
    contact_email : Optional[str] = None

class SupplierCreate(SupplierBase):
    pass

class SupplierOut(SupplierBase):
    id : int
    class config:
        from_attributes = True

class ProductBase(BaseModel):
    name : str
    sku : str
    category_id : int
    supplier_id : int
    reorder_level : int = 10
    unit_price : float = 0.10

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id : int
    class config:
        from_attributes = True

class StockMovementCreate(BaseModel):
    product_id : int
    quantity : int
    movement_type : MovementType

class StockMovementOut(StockMovementCreate):
    id : int
    timestamp : datetime
    class config:
        from_attributes = True

class InventoryOut(BaseModel):
    product_id : int
    current_stock : int
    class config:
        from_attributes : True

class SaleCreate(BaseModel):
    product_id : int
    quantity : int

class SaleOut(SaleCreate):
    id : int
    timestamp : datetime
    class config:
        from_attributes = True

class AssistantQuery(BaseModel):
    question : str