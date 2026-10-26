from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime
from models import MovementType


# ---------- Category ----------
class CategoryBase(BaseModel):
    name: str


class CategoryCreate(CategoryBase):
    pass


class CategoryOut(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Supplier ----------
class SupplierBase(BaseModel):
    name: str
    contact_email: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierOut(SupplierBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Product ----------
class ProductBase(BaseModel):
    name: str = Field(min_length=1)
    sku: str = Field(min_length=1)
    category_id: int
    supplier_id: Optional[int] = None
    reorder_level: int = Field(default=10, ge=0)
    unit_price: float = Field(gt=0)  # no default: price must be given
    image_url: Optional[str] = None


class ProductCreate(ProductBase):
    initial_stock: int = Field(default=0, ge=0)  # units on the shelf when the product is added


class ProductOut(ProductBase):
    id: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Stock movement ----------
class StockMovementCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)
    movement_type: MovementType


class StockMovementOut(StockMovementCreate):
    id: int
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)


# ---------- Inventory ----------
class InventoryOut(BaseModel):
    product_id: int
    current_stock: int
    model_config = ConfigDict(from_attributes=True)


# ---------- Sale ----------
class SaleCreate(BaseModel):
    product_id: int
    quantity: int = Field(gt=0)


class SaleOut(SaleCreate):
    id: int
    sale_date: datetime  # was `timestamp`; the Sale model column is sale_date
    model_config = ConfigDict(from_attributes=True)


# ---------- Assistant ----------
class AssistantQuery(BaseModel):
    question: str = Field(min_length=1, max_length=500)


# ---------- Catalog (one card on the inventory page) ----------
class Catalogitem(BaseModel):
    id: int
    name: str
    sku: str
    image_url: Optional[str] = None
    unit_price: float
    reorder_level: int
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    current_stock: int