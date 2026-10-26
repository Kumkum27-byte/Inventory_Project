import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta, timezone
from database import SessionLocal, engine, Base
import models

random.seed(42)  # reproducible data
DAYS = 90

CATEGORIES = ['Electronics', 'Groceries', 'Stationery']
SUPPLIERS = [
    ('Acme Traders', 'sales@acmetraders.example'),
    ('Bharat Supplies', 'orders@bharatsupplies.example'),
    ('Delta Wholesale', 'contact@deltawholesale.example'),
]
CATALOG = [  # (name, category, unit_price)
    ('Wireless Mouse', 'Electronics', 499),
    ('USB Cable', 'Electronics', 149),
    ('Earphones', 'Electronics', 799),
    ('Basmati Rice 5kg', 'Groceries', 450),
    ('Sunflower Oil 1L', 'Groceries', 180),
    ('Tea Powder 500g', 'Groceries', 250),
    ('Notebook A4', 'Stationery', 60),
    ('Gel Pen Pack', 'Stationery', 90),
    ('Stapler', 'Stationery', 120),
    ('Highlighter Set', 'Stationery', 150),
]

Base.metadata.create_all(bind=engine)
db = SessionLocal()

try:
    if db.query(models.Product).first():
        print("Data already exists. Clear the tables first, then re-run.")
        sys.exit(0)

    cats = {n: models.Category(name=n) for n in CATEGORIES}
    sups = [models.Supplier(name=n, contact_email=e) for n, e in SUPPLIERS]
    db.add_all(list(cats.values()) + sups)
    db.flush()

    start = datetime.now(timezone.utc) - timedelta(days=DAYS)
    total_sales = 0

    for name, cat, price in CATALOG:
        p = models.Product(
            name=name,
            sku=f"SKU{1000 + CATALOG.index((name, cat, price))}",
            category_id=cats[cat].id,
            supplier_id=random.choice(sups).id,
            reorder_level=random.randint(20, 60),
            unit_price=price,
        )
        db.add(p)
        db.flush()

        base = random.uniform(3, 12)   # this product's typical daily demand
        stock = 500
        db.add(models.StockMovement(
            product_id=p.id, movement_type=models.MovementType.stock_in,
            quantity=stock, timestamp=start))

        for day in range(DAYS):
            date = start + timedelta(days=day + 1)
            weekly = 1.4 if date.weekday() >= 5 else 1.0   # weekend uplift
            trend = 1 + 0.004 * day                          # slow growth
            qty = max(0, round(random.gauss(base * weekly * trend, base * 0.25)))
            qty = min(qty, stock)

            if qty > 0:
                db.add(models.Sale(product_id=p.id, quantity=qty, sale_date=date))
                db.add(models.StockMovement(
                    product_id=p.id, movement_type=models.MovementType.stock_out,
                    quantity=qty, timestamp=date))
                stock -= qty
                total_sales += 1

            if stock <= p.reorder_level:   # restock when low
                db.add(models.StockMovement(
                    product_id=p.id, movement_type=models.MovementType.stock_in,
                    quantity=500, timestamp=date))
                stock += 500

        db.add(models.Inventory(product_id=p.id, current_stock=stock))

    db.commit()
    print(f"Seed data inserted: {len(CATALOG)} products, {total_sales} sales rows.")
finally:
    db.close()