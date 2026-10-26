# app_streamlit.py
import os
import requests
import pandas as pd
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
TIMEOUT = 30

st.set_page_config(page_title="Inventory Dashboard", layout="wide")
st.title("📦 Inventory & Demand Forecasting Dashboard")


def api(method, path, **kwargs):
    """Call the backend. Returns (ok, data_or_error_message)."""
    try:
        res = requests.request(method, f"{API_URL}{path}", timeout=TIMEOUT, **kwargs)
    except requests.exceptions.RequestException:
        return False, f"Cannot reach the API at {API_URL}. Is the FastAPI server running?"
    try:
        body = res.json()
    except ValueError:
        body = res.text
    if res.ok:
        return True, body
    detail = body.get("detail", body) if isinstance(body, dict) else body
    if isinstance(detail, list):  # FastAPI validation errors
        detail = "; ".join(
            f"{'.'.join(str(x) for x in e.get('loc', [])[1:])}: {e.get('msg')}" for e in detail
        )
    return False, str(detail)


tab_prod, tab_inv, tab_move, tab_sale, tab_low, tab_fc, tab_ai = st.tabs([
    "Products", "Inventory", "Stock Movement", "Sales",
    "Low Stock Alerts", "Forecast", "Ask Copilot",
])

# ============ PART 1: ACTIONS (forms that change data) ============
# Forms run first, so every table below is fetched AFTER the change
# and always shows fresh data.

with tab_prod:
    st.subheader("Add Product")
    with st.form("add_product"):
        name = st.text_input("Product Name")
        sku = st.text_input("SKU")
        category_id = st.number_input("Category ID", min_value=1, step=1)
        supplier_id = st.number_input("Supplier ID", min_value=1, step=1)
        reorder_level = st.number_input("Reorder Level", min_value=0, value=10)
        unit_price = st.number_input("Unit Price", min_value=0.01, value=100.0)
        if st.form_submit_button("Create Product"):
            ok, out = api("POST", "/products/", json={
                "name": name, "sku": sku, "category_id": int(category_id),
                "supplier_id": int(supplier_id), "reorder_level": int(reorder_level),
                "unit_price": float(unit_price),
            })
            if ok:
                st.success("Product created!")
            else:
                st.error(out)

ok, products = api("GET", "/products/")
if not ok:
    st.error(products)
    st.stop()
products_df = pd.DataFrame(products)
names = {p["id"]: f'{p["name"]} ({p["sku"]})' for p in products}

with tab_move:
    st.subheader("Record Stock Movement")
    if not names:
        st.info("Add a product first.")
    else:
        with st.form("stock_movement"):
            pid = st.selectbox("Product", list(names), format_func=names.get, key="move_product")
            movement_type = st.selectbox("Type", ["stock_in", "stock_out"], key="move_type")
            quantity = st.number_input("Quantity", min_value=1, step=1, key="move_qty")
            if st.form_submit_button("Submit"):
                ok, out = api("POST", "/inventory/stock-movement", json={
                    "product_id": pid, "movement_type": movement_type, "quantity": int(quantity),
                })
                if ok:
                    st.success("Stock updated!")
                else:
                    st.error(out)

with tab_sale:
    st.subheader("Record Sale")
    if not names:
        st.info("Add a product first.")
    else:
        with st.form("sale"):
            pid = st.selectbox("Product", list(names), format_func=names.get, key="sale_product")
            quantity = st.number_input("Quantity sold", min_value=1, step=1, key="sale_qty")
            if st.form_submit_button("Record Sale"):
                ok, out = api("POST", "/sales/", json={"product_id": pid, "quantity": int(quantity)})
                if ok:
                    st.success("Sale recorded, stock reduced!")
                else:
                    st.error(out)

# ============ PART 2: DISPLAY (fetched after any change above) ============

ok_i, inv = api("GET", "/inventory/")
inv_df = pd.DataFrame(inv) if ok_i and inv else pd.DataFrame(columns=["product_id", "current_stock"])
ok_s, sales = api("GET", "/sales/")
sales_df = pd.DataFrame(sales) if ok_s and sales else pd.DataFrame()

with tab_prod:
    st.subheader("All Products")
    st.dataframe(products_df, use_container_width=True)

with tab_inv:
    st.subheader("Current Stock Levels")
    if inv_df.empty or products_df.empty:
        st.info("No inventory yet.")
    else:
        view = inv_df.merge(
            products_df[["id", "name", "sku", "reorder_level"]],
            left_on="product_id", right_on="id"
        ).drop(columns="id")
        view["status"] = view.apply(
            lambda r: "⚠️ Low" if r["current_stock"] <= r["reorder_level"] else "OK", axis=1
        )
        st.dataframe(
            view[["product_id", "name", "sku", "current_stock", "reorder_level", "status"]],
            use_container_width=True,
        )

with tab_sale:
    st.subheader("Recent Sales")
    if sales_df.empty:
        st.info("No sales yet.")
    else:
        st.dataframe(sales_df.sort_values("id", ascending=False).head(20), use_container_width=True)

with tab_low:
    st.subheader("Products Needing Reorder")
    ok_l, low = api("GET", "/inventory/low-stock")
    if not ok_l:
        st.error(low)
    elif low:
        st.dataframe(pd.DataFrame(low), use_container_width=True)
    else:
        st.info("No products below reorder level right now.")

with tab_fc:
    st.subheader("Demand Forecast")
    if not names:
        st.info("Add a product first.")
    else:
        c1, c2 = st.columns(2)
        pid = c1.selectbox("Product", list(names), format_func=names.get, key="fc_product")
        horizon = c2.selectbox("Horizon (days)", [7, 30, 90], key="fc_horizon")
        if st.button("Generate forecast"):
            ok, fc = api("GET", f"/forecasts/{pid}", params={"horizon": horizon})
            if not ok:
                st.error(fc)
            else:
                fc_df = pd.DataFrame(fc["forecast"])
                fc_df["date"] = pd.to_datetime(fc_df["date"])
                fc_series = fc_df.set_index("date")["predicted_quantity"].rename("Forecast")

                actual = pd.Series(dtype=float)
                if not sales_df.empty:
                    s = sales_df[sales_df["product_id"] == pid].copy()
                    if not s.empty:
                        s["day"] = (pd.to_datetime(s["sale_date"], utc=True)
                                    .dt.tz_localize(None).dt.normalize())
                        actual = s.groupby("day")["quantity"].sum().tail(30).rename("Actual")

                chart = fc_series.to_frame() if actual.empty else pd.concat([actual, fc_series], axis=1)
                st.line_chart(chart)

                stock_row = inv_df[inv_df["product_id"] == pid]
                current_stock = int(stock_row["current_stock"].iloc[0]) if not stock_row.empty else 0
                reorder = int(products_df.loc[products_df["id"] == pid, "reorder_level"].iloc[0])
                demand = float(fc["total_predicted_demand"])
                suggested = max(0, round(demand + reorder - current_stock))

                m1, m2, m3 = st.columns(3)
                m1.metric("Current stock", current_stock)
                m2.metric(f"Predicted demand ({horizon} days)", round(demand, 1))
                m3.metric("Suggested order qty", suggested)
                st.caption(
                    "Suggested order = predicted demand + reorder level - current stock. "
                    "A simple rule; supplier lead time is not modelled."
                )

with tab_ai:
    st.subheader("Ask the Inventory Copilot")
    question = st.text_input(
        "Ask a question",
        placeholder="e.g. which products are low on stock?",
        key="ai_question",
    )
    if st.button("Ask"):
        if not question.strip():
            st.warning("Please type a question first.")
        else:
            with st.spinner("Thinking..."):
                ok, out = api("POST", "/assistant/query", json={"question": question})
            if ok:
                st.success(out["answer"])
            else:
                st.error(out)