import random
import time
import requests

API = "http://127.0.0.1:8000"

products = requests.get(f"{API}/products/", timeout=10).json()
if not products:
    raise SystemExit("No products found. Run data/seed_data.py first.")

# some products sell more than others, so the Top 5 looks realistic
weights = [random.uniform(1, 5) for _ in products]

print(f"Simulating sales for {len(products)} products. Ctrl+C to stop.")
while True:
    p = random.choices(products, weights=weights)[0]
    qty = random.randint(1, 3)
    r = requests.post(f"{API}/sales/", json={"product_id": p["id"], "quantity": qty}, timeout=10)

    if r.ok:
        print(f"sold {qty} x {p['name']}")
    elif r.status_code == 400:  # not enough stock: restock and carry on
        requests.post(
            f"{API}/inventory/stock-movement",
            json={"product_id": p["id"], "movement_type": "stock_in", "quantity": 100},
            timeout=10,
        )
        print(f"restocked {p['name']}")
    else:
        print("error:", r.status_code, r.text)

    time.sleep(random.uniform(2, 5))