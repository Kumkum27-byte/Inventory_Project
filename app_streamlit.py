# app_streamlit.py
import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Inventory Dashboard", layout="wide")
st.title("📦 Inventory & Demand Forecasting Dashboard")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Products", "Inventory", "Stock Movement", "Low Stock Alerts", "Ask Copilot"])

# ---------------- TAB 1: PRODUCTS ----------------
with tab1:
    st.subheader("Add Product")
    with st.form("add_product"):
        name = st.text_input("Product Name")
        sku = st.text_input("SKU")
        category_id = st.number_input("Category ID", min_value=1, step=1)
        supplier_id = st.number_input("Supplier ID", min_value=1, step=1)
        reorder_level = st.number_input("Reorder Level", min_value=0, value=10)
        unit_price = st.number_input("Unit Price", min_value=0.0, value=0.0)
        submitted = st.form_submit_button("Create Product")
        if submitted:
            payload = {
                "name": name, "sku": sku, "category_id": category_id,
                "supplier_id": supplier_id, "reorder_level": reorder_level,
                "unit_price": unit_price
            }
            res = requests.post(f"{API_URL}/products/", json=payload)
            if res.status_code == 200:
                st.success("Product created!")
            else:
                st.error(res.json())

    st.subheader("All Products")
    res = requests.get(f"{API_URL}/products/")
    if res.status_code == 200:
        df = pd.DataFrame(res.json())
        st.dataframe(df, use_container_width=True)

# ---------------- TAB 2: INVENTORY ----------------
with tab2:
    st.subheader("Current Stock Levels")
    res = requests.get(f"{API_URL}/inventory/")
    if res.status_code == 200:
        df = pd.DataFrame(res.json())
        st.dataframe(df, use_container_width=True)

# ---------------- TAB 3: STOCK MOVEMENT ----------------
with tab3:
    st.subheader("Record Stock Movement")
    with st.form("stock_movement"):
        product_id = st.number_input("Product ID", min_value=1, step=1)
        movement_type = st.selectbox("Type", ["stock_in", "stock_out"])
        quantity = st.number_input("Quantity", min_value=1, step=1)
        submitted = st.form_submit_button("Submit")
        if submitted:
            payload = {"product_id": product_id, "movement_type": movement_type, "quantity": quantity}
            res = requests.post(f"{API_URL}/inventory/stock-movement", json=payload)
            if res.status_code == 200:
                st.success("Stock updated!")
            else:
                st.error(res.json())

# ---------------- TAB 4: LOW STOCK ----------------
with tab4:
    st.subheader("Products Needing Reorder")
    res = requests.get(f"{API_URL}/inventory/low-stock")
    if res.status_code == 200:
        data = res.json()
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("No products below reorder level right now.")

# -----------------TAB 5 : ASSISTANT---------------------
# ---------------- TAB 5: ASK COPILOT ----------------
with tab5:
    st.subheader("Ask the Inventory Copilot")
    question = st.text_input("Ask a question (e.g. 'which products are low on stock?')")
    if st.button("Ask"):
        if question:
            res = requests.post(f"{API_URL}/assistant/query", json={"question": question})
            if res.status_code == 200:
                st.success(res.json()["answer"])
            else:
                st.error(res.json())
        else:
            st.warning("Please type a question first.")