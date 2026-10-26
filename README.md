# Inventory & Demand Forecasting System

A full-stack inventory management application with a FastAPI backend, a Next.js dashboard, ML-based demand forecasting, and an optional Gemini-powered inventory copilot. A Streamlit dashboard is also included as an alternative UI.

## Features

- **Inventory management:** Manage products, categories, and suppliers; track stock movements and sales with automatic inventory updates.
- **Next.js dashboard:** View product and stock summaries, daily sales, top-selling products, demand forecasts, and low-stock reorder plans.
- **Inventory page:** Browse products by category, add products, record a sale, and restock items.
- **Demand forecasting:** An XGBoost model predicts demand for 7, 30, or 90 days using historical sales.
- **Inventory copilot:** Ask questions about low stock, demand forecasts, and slow-moving products using grounded inventory data.
- **Streamlit dashboard:** An alternate interface for product, stock, sales, forecast, and copilot workflows.

## Tech stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **Frontend:** Next.js, React, TypeScript, Tailwind CSS, Recharts
- **Forecasting:** XGBoost, pandas, scikit-learn, joblib
- **Copilot:** Google Gemini API
- **Alternative UI:** Streamlit

## Requirements

- Python and pip
- PostgreSQL
- Node.js and npm (for the Next.js frontend)
- A Google Gemini API key (optional; required only for copilot answers)

## Setup

### 1. Configure the database

Create a PostgreSQL database, then create a `.env` file in the repository root:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:PORT/DATABASE
GOOGLE_API_KEY=your_google_api_key
# Optional; defaults to gemini-2.5-flash
GEMINI_MODEL=gemini-2.5-flash
```

`GOOGLE_API_KEY` is only needed when using the copilot. Keep `.env` private; it is excluded from Git.

### 2. Install backend dependencies and prepare sample data

Run these commands from the repository root:

```bash
pip install -r requirements.txt
python data/seed_data.py
python forecasting/train_model.py
```

The seed script creates sample categories, suppliers, products, inventory, and 90 days of sales history. It exits without reseeding if products already exist. The training script reads sales from the database and writes the generated model to `forecasting/demand_model.pkl`.

### 3. Start the API

From the repository root, run:

```bash
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### 4. Start the Next.js frontend

In a second terminal:

```bash
cd frontend
npm ci
npm run dev
```

Open `http://localhost:3000`. The frontend uses `http://127.0.0.1:8000` by default. To point it to another API URL, set `NEXT_PUBLIC_API_URL` in `frontend/.env.local`, for example:

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

The API's CORS configuration currently permits the local frontend origins `http://localhost:3000` and `http://127.0.0.1:3000`.

### Optional: run the Streamlit dashboard

With the API running, start the alternate dashboard from the repository root:

```bash
streamlit run app_streamlit.py
```

It uses `http://127.0.0.1:8000` by default. Set the `API_URL` environment variable if the API is hosted elsewhere.

## API overview

| Area | Routes |
| --- | --- |
| Products | `GET /products/`, `GET /products/{product_id}`, `POST /products/` |
| Categories | `GET /categories/`, `POST /categories/` |
| Suppliers | `GET /suppliers/`, `POST /suppliers/` |
| Inventory | `GET /inventory/`, `GET /inventory/catalog`, `GET /inventory/low-stock`, `GET /inventory/reorder-plan`, `POST /inventory/stock-movement` |
| Sales | `GET /sales/`, `POST /sales/`, `GET /sales/daily`, `GET /sales/daily/{product_id}`, `GET /sales/top-products` |
| Forecasts | `GET /forecasts/{product_id}?horizon=7` (supported horizons: 7, 30, or 90 days) |
| Copilot | `POST /assistant/query` |

See `/docs` on the running API for request and response schemas and query parameters.

## Utility scripts

- `python reset_db.py` drops and recreates all database tables. **This permanently deletes the existing application data.**
- `python simulate_sales.py` continuously posts simulated sales to a running API; stop it with Ctrl+C.
