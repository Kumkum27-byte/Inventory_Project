from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
import models  # noqa: F401  (registers every table before create_all)
from routers import products, supplier, category, inventory, sales, forecast, assistant

# Tables create karne ke liye
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory & Demand Forecasting API")

# Lets the Next.js app (a different origin) call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(supplier.router)
app.include_router(category.router)
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(forecast.router)
app.include_router(assistant.router)