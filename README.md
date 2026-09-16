# Inventory & Demand Forecasting System

A full-stack inventory management system with ML-based demand forecasting and a GenAI-powered copilot.

## Features

- **Inventory Management** — Product, category, and supplier CRUD; stock-in/stock-out tracking with automatic stock sync
- **Demand Forecasting** — XGBoost model predicting product demand over 7/30/90-day horizons using lag and calendar features
- **GenAI Copilot** — Natural language Q&A grounded in live inventory data (low-stock alerts, forecasts, slow-moving products)

## Tech Stack

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **ML:** XGBoost, scikit-learn
- **GenAI:** Google Gemini API
- **Frontend:** Streamlit

## Setup

1. Install dependencies: pip install -r requirements.txt
2. Set up `.env` with `DATABASE_URL` and `GEMINI_API_KEY`
3. Create the Postgres database
4. Run the API: uvicorn main:app --reload
5. Seed sample data: python data/seed_data.py
6. Train the forecasting model: python forecasting/train_model.py
7. Run the dashboard: streamlit run app_streamlit.py

## API Endpoints

- `POST /products/`, `GET /products/`
- `POST /inventory/stock-movement`, `GET /inventory/`, `GET /inventory/low-stock`
- `GET /forecasts/{product_id}?horizon=7`
- `POST /assistant/query`
