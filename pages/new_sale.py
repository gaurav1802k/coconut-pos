import streamlit as st
from datetime import datetime
from zoneinfo import ZoneInfo

from database import (
    init_database,
    get_customers,
    add_customer,
    get_products,
    add_product,
    create_sale,
)

from excel_export import export_all_to_excel
from theme import apply_theme, build_sidebar


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="New Sale",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# INITIALIZE
# =========================================================

init_database()
apply_theme()
build_sidebar()


# =========================================================
# HEADER
# =========================================================

st.title("🧾 New Sale")

st.caption(
    "Create a new customer transaction and record payment."
)

st.divider()


# =========================================================
# CUSTOMER
# =========================================================

st.subheader("👤 Customer Details")

# These three customers are used frequently, so keep them
# available as one-tap buttons. add_customer() is safe here:
# if the customer already exists, it simply returns the
# existing customer ID instead of creating a duplicate.
fixed_customer_names = [
    "Raju",
    "Harvali",
    "Bhakt",
]

for fixed_name in fixed_customer_names:
    add_customer(fixed_name, "")

customers = get_customers()

customer_options = {
    "➕ New Customer": None
}

for customer in customers:

    label = (
        f"{customer['name']} • "
        f"{customer['phone'] or 'No phone'}"
    )

    customer_options[label] = customer["id"]


# Build the exact labels used by the quick buttons.
fixed_customer_labels = {}

for fixed_name in fixed_customer_names:

    fixed_customer = next(
        (
            customer
            for customer in customers
            if customer["name"].strip().lower()
            == fixed_name.lower()
        ),
        None,
    )

    if fixed_customer is not None:

        fixed_customer_labels[fixed_name] = (
            f"{fixed_customer['name']} • "
            f"{fixed_customer['phone'] or 'No phone'}"
        )


# Remember the selected customer across Streamlit reruns.
if "selected_customer_label" not in st.session_state:

    st.session_state["selected_customer_label"] = (
        "➕ New Customer"
    )


# =========================================================
# ONE-TAP FIXED CUSTOMERS
# =========================================================

st.caption("⚡ Quick Select")

quick_cols = st.columns(3)

for col, fixed_name in zip(
    quick_cols,
    fixed_customer_names,
):

    with col:

        if st.button(
            f"👤 {fixed_name}",
            key=f"quick_customer_{fixed_name.lower()}",
            use_container_width=True,
        ):

            fixed_label = fixed_customer_labels.get(
                fixed_name
            )

            if fixed_label in customer_options:

                st.session_state[
                    "selected_customer_label"
                ] = fixed_label

            st.rerun()


# =========================================================
# CUSTOMER SELECT
# =========================================================

saved_label = st.session_state[
    "selected_customer_label"
]

if saved_label not in customer_options:

    saved_label = "➕ New Customer"

selected_customer = st.selectbox(
    "Select Customer",
    list(customer_options.keys()),
    index=list(customer_options.keys()).index(
        saved_label
    ),
)

# Keep the selection remembered.
st.session_state["selected_customer_label"] = (
    selected_customer
)


# =========================================================
# NEW CUSTOMER
# =========================================================

if customer_options[selected_customer] is None:

    col1, col2 = st.columns(2)

    with col1:

        customer_name = st.text_input(
            "Customer Name",
            placeholder="Enter customer name",
        )

    with col2:

        customer_phone = st.text_input(
            "Phone Number",
            placeholder="Optional",
        )

else:

    customer_id = customer_options[
        selected_customer
    ]

    selected_customer_data = next(
        c
        for c in customers
        if c["id"] == customer_id
    )

    customer_name = (
        selected_customer_data["name"]
    )

    customer_phone = (
        selected_customer_data["phone"]
        or ""
    )

    st.success(
        f"Selected customer: {customer_name}"
    )


st.divider()


# =========================================================
# EXCEPTIONAL ITEM
# =========================================================

st.subheader("➕ Exceptional Item")

with st.expander(
    "Add an item that is not already in the list"
):

    col1, col2, col3 = st.columns(
        [2, 1, 1]
    )

    with col1:

        exceptional_name = st.text_input(
            "Item Name",
            placeholder="Example: Special Pooja Item",
            key="exceptional_name",
        )

    with col2:

        exceptional_price = st.number_input(
            "Price ₹",
            min_value=0.0,
            step=1.0,
            key="exceptional_price",
        )

    with col3:

        st.write("")
        st.write("")

        if st.button(
            "➕ Add Item",
            use_container_width=True,
        ):

            try:

                add_product(
                    exceptional_name,
                    exceptional_price,
                )

                st.success(
                    "Item added successfully."
                )

                st.rerun()

            except Exception as e:

                st.error(
                    str(e)
                )


st.divider()


# =========================================================
# ITEMS
# =========================================================

st.subheader("🛒 Select Items")

st.caption(
    "Select the quantity for each product."
)

products = get_products(
    active_only=True
)

selected_items = []


# =========================================================
# PRODUCT GRID
# =========================================================

for i in range(
    0,
    len(products),
    3
):

    cols = st.columns(3)

    for col, product in zip(
        cols,
        products[i:i + 3]
    ):

        with col:

            with st.container(
                border=True
            ):

                st.markdown(
                    f"### {product['name']}"
                )

                st.caption(
                    f"₹{float(product['price']):,.2f} per item"
                )

                quantity = st.number_input(
                    "Quantity",
                    min_value=0,
                    step=1,
                    value=0,
                    key=f"quantity_{product['id']}",
                )

                if quantity > 0:

                    subtotal = (
                        quantity
                        * float(product["price"])
                    )

                    st.success(
                        f"Subtotal: ₹{subtotal:,.2f}"
                    )

                    selected_items.append(
                        {
                            "product_id": product["id"],
                            "name": product["name"],
                            "quantity": quantity,
                            "price": float(product["price"]),
                            "subtotal": subtotal,
                        }
                    )


st.divider()


# =========================================================
# BILL SUMMARY
# =========================================================

st.subheader("🧾 Bill Summary")


if selected_items:

    total = sum(
        item["subtotal"]
        for item in selected_items
    )

    for item in selected_items:

        col1, col2, col3 = st.columns(
            [3, 1, 1]
        )

        with col1:

            st.write(
                f"**{item['name']}**"
            )

        with col2:

            st.write(
                f"× {item['quantity']}"
            )

        with col3:

            st.write(
                f"₹{item['subtotal']:,.2f}"
            )

else:

    total = 0.0

    st.info(
        "No items selected yet."
    )


st.markdown(
    f"## Total Amount: ₹{total:,.2f}"
)

st.divider()


# =========================================================
# PAYMENT
# =========================================================

st.subheader("💰 Payment")

# The button writes to a separate session-state value through a callback.
# This avoids changing a widget's own key after st.number_input() has been
# created, which causes StreamlitAPIException.
if "payment_amount" not in st.session_state:
    st.session_state["payment_amount"] = 0.0


def set_full_payment():
    st.session_state["payment_amount"] = float(total)


# Make sure an older amount never exceeds the current bill.
if st.session_state["payment_amount"] > float(total):
    st.session_state["payment_amount"] = float(total)

pay_col1, pay_col2 = st.columns([2.2, 1])

with pay_col1:
    received_amount = st.number_input(
        "Amount Received ₹",
        min_value=0.0,
        max_value=float(total),
        step=1.0,
        key="payment_amount",
        disabled=(total <= 0),
    )

with pay_col2:
    st.write("")
    st.write("")

    st.button(
        "✅ PAID",
        use_container_width=True,
        type="primary",
        disabled=(total <= 0),
        key="quick_paid_button",
        on_click=set_full_payment,
    )


remaining = max(
    total - received_amount,
    0.0,
)


if received_amount <= 0:

    payment_status = "Unpaid"

elif received_amount < total:

    payment_status = "Partially Paid"

else:

    payment_status = "Paid"


col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "Total",
        f"₹{total:,.2f}",
    )


with col2:

    st.metric(
        "Received",
        f"₹{received_amount:,.2f}",
    )


with col3:

    st.metric(
        "Remaining",
        f"₹{remaining:,.2f}",
    )


if payment_status == "Paid":

    st.success(
        "✅ Payment Status: PAID",
    )

elif payment_status == "Partially Paid":

    st.warning(
        "🟡 Payment Status: PARTIALLY PAID",
    )

else:

    st.error(
        "🔴 Payment Status: UNPAID",
    )


if received_amount > 0:

    payment_method = st.radio(
        "Payment Method",
        [
            "Cash",
            "UPI",
            "Other",
        ],
        horizontal=True,
    )

else:

    payment_method = None


st.divider()

# =========================================================
# NOTES
# =========================================================

st.subheader("📝 Notes")

notes = st.text_input(
    "Optional note",
    placeholder="Example: Family order / special request",
)


st.divider()


# =========================================================
# SAVE SALE
# =========================================================

if st.button(
    "💾 SAVE SALE",
    use_container_width=True,
    type="primary",
):

    # -----------------------------------------------------
    # CUSTOMER VALIDATION
    # -----------------------------------------------------

    if customer_options[selected_customer] is None:

        if not customer_name.strip():

            st.error(
                "Please enter a customer name."
            )

            st.stop()

        try:

            customer_id = add_customer(
                customer_name,
                customer_phone,
            )

        except Exception as e:

            st.error(
                f"Customer error: {e}"
            )

            st.stop()


    # -----------------------------------------------------
    # ITEM VALIDATION
    # -----------------------------------------------------

    if total <= 0:

        st.error(
            "Please select at least one item."
        )

        st.stop()


    # -----------------------------------------------------
    # SAVE SALE
    # -----------------------------------------------------

    try:

        sale_id = create_sale(
            customer_id=customer_id,
            items=selected_items,
            received_amount=received_amount,
            payment_method=payment_method,
            note=notes,
        )


        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        st.success(
            f"✅ Sale #{sale_id} saved successfully!"
        )

        st.info(
            f"Customer: {customer_name}"
        )

        st.write(
            f"💰 Total: ₹{total:,.2f}"
        )

        st.write(
            f"✅ Received: ₹{received_amount:,.2f}"
        )

        st.write(
            f"⚠️ Remaining: ₹{remaining:,.2f}"
        )

        st.write(
            f"💳 Status: {payment_status}"
        )


        # -------------------------------------------------
        # EXCEL
        # -------------------------------------------------

        try:

            excel_path = export_all_to_excel()

            st.write(
                f"📊 Excel updated: "
                f"{excel_path.name}"
            )

        except Exception as excel_error:

            st.warning(
                "Sale was saved, but Excel could "
                f"not be updated: {excel_error}"
            )


        # -------------------------------------------------
        # TIMESTAMP
        # -------------------------------------------------

        saved_time = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime(
            "%d-%m-%Y %I:%M:%S %p"
        )

        st.write(
            f"🕐 Saved at: {saved_time}"
        )


    except Exception as e:

        st.error(
            f"Could not save sale: {e}"
        )