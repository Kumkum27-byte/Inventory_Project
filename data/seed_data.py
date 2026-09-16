import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import random
from datetime import datetime, timedelta
from faker import Faker
from database import SessionLocal
import models

fake = Faker()
db = SessionLocal()

#3 categories, 3 suppliers
categories = [models.Category(name=n) for n in ['Electronics', 'Groceries', 'Stationery']]
suppliers = [models.Supplier(name=fake.company(), contact_email=fake.email()) for _ in range(3)]
db.add_all(categories + suppliers)
db.commit()

#10 products
products = []
for i in range(10):
    p = models.Product(
        name = fake.word().capitalize() + " " + fake.word().capitalize(),
        sku = f"SKU{1000 + i}",
        category_id = random.choice(categories).id,
        supplier_id =  random.choice(suppliers).id,
        reorder_level = random.randint(5, 20),
        unit_price = round(random.uniform(50, 500), 2)
    )

    db.add(p)
    products.append(p)
    db.commit()

#har product ke liye inventory row + 90 days ki sales history
for p in products:
    inv =  models.Inventory(product_id=p.id, current_stock=random.randint(50, 200))
    db.add(inv)

    for day in range(90):
        date = datetime.now() - timedelta(days = 90-day)
        if random.random() < 0.7: #har din sale nii hoti
            qty = random.randint(1,10)
            db.add(models.Sale(product_id=p.id, quantity=qty, sale_date=date))

db.commit()
print("Seed data insereted successfully")
db.close()