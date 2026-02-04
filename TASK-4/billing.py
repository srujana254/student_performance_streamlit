import datetime as dt
import pandas as pd
import streamlit as st

from database import (
    add_bill_item,
    add_product,
    create_bill,
    daily_sales_summary,
    fetch_products,
    init_db,
    update_stock,
)


st.set_page_config(page_title="Inventory & Billing", layout="wide")
init_db()

if "cart" not in st.session_state:
    st.session_state.cart = []


def product_lookup():
    products = fetch_products()
    return {
        f"{name} (₹{price}) - Stock {stock}": (pid, name, float(price), stock)
        for pid, name, price, stock in products
    }


def add_to_cart(product, qty):
    pid, name, price, stock = product
    if qty <= 0:
        st.error("Quantity must be greater than 0")
        return
    if qty > stock:
        st.error("Not enough stock")
        return
    st.session_state.cart.append(
        {"product_id": pid, "name": name, "price": price, "qty": qty}
    )


def cart_total():
    return sum(item["price"] * item["qty"] for item in st.session_state.cart)


def cart_dataframe():
    if not st.session_state.cart:
        return pd.DataFrame(columns=["Product", "Price", "Quantity", "Total"])
    rows = [
        {
            "Product": item["name"],
            "Price": item["price"],
            "Quantity": item["qty"],
            "Total": item["price"] * item["qty"],
        }
        for item in st.session_state.cart
    ]
    return pd.DataFrame(rows)


def generate_bill_text(bill_id, bill_date, total_amount, df):
    lines = [
        "Inventory & Billing System",
        f"Bill ID: {bill_id}",
        f"Date: {bill_date}",
        "",
        df.to_string(index=False),
        "",
        f"Total Amount: ₹{total_amount:.2f}",
    ]
    return "\n".join(lines) + "\n"


st.title("🧾 Inventory & Billing Management")
tab1, tab2, tab3 = st.tabs(["Add Product", "Billing", "Daily Sales"])

with tab1:
    st.subheader("➕ Add Products")
    col1, col2, col3 = st.columns(3)
    with col1:
        name = st.text_input("Product Name")
    with col2:
        price = st.number_input("Price", min_value=0.0, step=0.5)
    with col3:
        stock = st.number_input("Stock", min_value=0, step=1)
    if st.button("Add Product", use_container_width=True):
        if not name:
            st.error("Enter product name")
        else:
            add_product(name, price, stock)
            st.success("Product added")

with tab2:
    st.subheader("🛒 Create Bill")
    products_map = product_lookup()
    if not products_map:
        st.info("No products available. Add products first.")
    else:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            selected_label = st.selectbox("Select Product", list(products_map.keys()))
        with col2:
            qty = st.number_input("Quantity", min_value=1, step=1)
        with col3:
            st.write("")
            if st.button("Add to Cart", use_container_width=True):
                add_to_cart(products_map[selected_label], qty)

        st.markdown("---")
        df = cart_dataframe()
        st.dataframe(df, use_container_width=True)
        total = cart_total()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total", f"₹{total:.2f}")
        with col2:
            if st.button("Clear Cart", use_container_width=True):
                st.session_state.cart = []

        if st.button("Generate Bill", use_container_width=True) and not df.empty:
            bill_date = dt.date.today()
            bill_id = create_bill(bill_date, total)
            for item in st.session_state.cart:
                add_bill_item(bill_id, item["product_id"], item["qty"])
            for pid, name, price, stock in fetch_products():
                for item in st.session_state.cart:
                    if item["product_id"] == pid:
                        update_stock(pid, stock - item["qty"])
            bill_text = generate_bill_text(bill_id, bill_date, total, df)
            st.success(f"Bill #{bill_id} generated")
            st.download_button(
                "Download Bill", bill_text, file_name=f"bill_{bill_id}.txt"
            )
            st.session_state.cart = []

with tab3:
    st.subheader("📅 Daily Sales Summary")
    date_value = st.date_input("Select Date", value=dt.date.today())
    count, total_sales = daily_sales_summary(date_value)
    col1, col2 = st.columns(2)
    col1.metric("Total Bills", int(count))
    col2.metric("Total Sales", f"₹{float(total_sales):.2f}")