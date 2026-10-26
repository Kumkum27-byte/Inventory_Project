from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name =  Column(String, unique=True, nullable=False)
    products = relationship('Product', back_populates='category')

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True, index=True)
    name =  Column(String, nullable=False)
    contact_email = Column(String)
    products = relationship('Product', back_populates='supplier')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    sku = Column(String, unique=True, nullable=False)
    category_id = Column(Integer, ForeignKey('categories.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    reorder_level = Column(Integer, default=10)
    unit_price = Column(Float, nullable=False)
    image_url = Column(String)      # link to the product image

    category = relationship("Category", back_populates='products')
    supplier = relationship("Supplier", back_populates='products')

class MovementType(str, enum.Enum):
    stock_in = 'stock_in'
    stock_out = 'stock_out'

class StockMovement(Base):
    __tablename__ = 'stock_movements'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    movement_type = Column(Enum(MovementType), nullable=False)
    quantity = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default = func.now())

    product = relationship("Product")

class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), unique=True)
    current_stock = Column(Integer, default=0)

    product = relationship("Product")

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    sale_date = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product")