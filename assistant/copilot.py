import json
import re
from fastapi import HTTPException
import models
from assistant.data_retrieval import (
    get_low_stock_products,
    get_forecast_summary,
    get_slow_moving_products,
)
from assistant.llm_client import ask_llm

ALLOWED_HORIZONS = (7, 30, 90)


def build_prompt(data, question: str) -> str:
    return f"Data:\n{json.dumps(data, indent=2, default=str)}\n\nQuestion: {question}\n\nAnswer:"


def find_product_id(question: str, db):
    """'product 3' / 'id 3' / '#3' first, then a product-name match."""
    m = re.search(r"\b(?:product|id)\s*#?\s*(\d+)|#(\d+)", question)
    if m:
        return int(m.group(1) or m.group(2))
    for p in db.query(models.Product).all():
        if p.name.lower() in question:
            return p.id
    return None


def find_horizon(question: str) -> int:
    """'next 30 days' -> 30. Only 7/30/90 are supported, default 7."""
    m = re.search(r"(\d+)\s*-?\s*days?", question)
    if m and int(m.group(1)) in ALLOWED_HORIZONS:
        return int(m.group(1))
    return 7


def ask_copilot(question: str, db):
    q = question.lower().strip()

    if any(k in q for k in ("low stock", "reorder", "running out", "running low", "out of stock")):
        data = get_low_stock_products(db)
        if not data:
            return "No products are currently at or below their reorder level."
        return ask_llm(build_prompt(data, question))

    if "predict" in q or "forecast" in q:
        product_id = find_product_id(q, db)
        if product_id is None:
            return "Please tell me which product, e.g. 'forecast for product 3' or use the product name."
        try:
            data = get_forecast_summary(product_id, horizon_days=find_horizon(q))
        except HTTPException as e:
            return e.detail  # e.g. "Product not found" becomes a chat answer
        return ask_llm(build_prompt(data, question))

    if "slow" in q:
        data = get_slow_moving_products(db)
        if not data:
            return "There are no products in the system yet."
        return ask_llm(build_prompt(data, question))

    return ("Sorry, I couldn't understand your question. "
            "Try asking about low stock, forecasts, or slow-moving products.")