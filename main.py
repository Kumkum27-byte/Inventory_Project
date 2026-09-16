from fastapi import FastAPI
from database import Base, engine
from routers import products, supplier, category, inventory, sales, forecast, assistant
from routers import category
from routers import forecast
from routers import inventory
from routers import products
from routers import sales

# Tables create karne ke liye
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory & Demand Forecasting API")

app.include_router(products.router)
app.include_router(supplier.router)
app.include_router(category.router)
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(forecast.router)
app.include_router(assistant.router)