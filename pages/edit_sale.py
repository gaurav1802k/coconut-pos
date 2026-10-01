import streamlit as st

from database import (
    init_database,
    get_sales,
    get_sale,
    get_sale_items
)

from excel_export import export_all_to_excel

from theme import (
    apply_theme,
    build_sidebar
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Edit Sale",
    page_icon="✏️",
    layout="wide"
)


# =========================================================
# INITIALIZE
# =========================================================

init_database()

apply_theme()
build_sidebar()


# =========================================================
# PAGE HEADER
# =========================================================

st.title("✏️ Edit Sale")

st.caption(
    "Review and manage an existing transaction."
)


# =========================================================
# SAFETY MESSAGE
# =========================================================

st.info(
    "Existing payment records are protected. "
    "Use this page to review a transaction before making changes."
)


# =========================================================
# LOAD SALES
# =========================================================

sales = get_sales(
    period="All Time"
)


if not sales:

    st.success(
        "No sales available."
    )

    st.stop()


# =========================================================
# SELECT SALE
# =========================================================

st.subheader(
    "Select Transaction"
)


sale_options = {}

for sale in sales:

    label = (
        f"Sale #{sale['id']}  |  "
        f"{sale['customer_name']}  |  "
        f"₹{sale['total']:,.2f}  |  "
        f"{sale['status']}"
    )

    sale_options[label] = sale["id"]


selected_label = st.selectbox(
    "Transaction",
    list(sale_options.keys())
)


sale_id = sale_options[
    selected_label
]


# =========================================================
# GET SELECTED SALE
# =========================================================

sale = get_sale(
    sale_id
)


if sale is None:

    st.error(
        "Transaction not found."
    )

    st.stop()


# =========================================================
# AMOUNTS
# =========================================================

total = float(
    sale["total"]
)

received = float(
    sale["received"]
)

remaining = max(
    total - received,
    0
)


# =========================================================
# SALE INFORMATION
# =========================================================

st.divider()

st.subheader(
    "Sale Information"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Sale ID",
        f"#{sale['id']}"
    )


with col2:

    st.metric(
        "Total",
        f"₹{total:,.2f}"
    )


with col3:

    st.metric(
        "Received",
        f"₹{received:,.2f}"
    )


with col4:

    st.metric(
        "Remaining",
        f"₹{remaining:,.2f}"
    )


# =========================================================
# CUSTOMER
# =========================================================

st.subheader(
    "👤 Customer"
)


col1, col2 = st.columns(2)


with col1:

    st.write(
        f"**Name:** {sale['customer_name']}"
    )


with col2:

    st.write(
        f"**Phone:** "
        f"{sale['phone'] or 'Not provided'}"
    )


st.write(
    f"🕐 **Date & Time:** "
    f"{sale['created_at']}"
)


st.write(
    f"💳 **Payment Status:** "
    f"{sale['payment_status']}"
)


st.divider()


# =========================================================
# CURRENT ITEMS
# =========================================================

st.subheader(
    "🛒 Current Items"
)

st.caption(
    "Items recorded in this transaction."
)


items = get_sale_items(
    sale_id
)


if items:

    for item in items:

        col1, col2, col3, col4 = st.columns(4)


        with col1:

            st.write(
                f"**{item['name']}**"
            )


        with col2:

            st.write(
                f"Quantity: "
                f"{item['quantity']}"
            )


        with col3:

            st.write(
                f"Price: "
                f"₹{float(item['price']):,.2f}"
            )


        with col4:

            st.write(
                f"Subtotal: "
                f"₹{float(item['subtotal']):,.2f}"
            )


else:

    st.info(
        "No items found for this sale."
    )


st.divider()


# =========================================================
# PAYMENT INFORMATION
# =========================================================

st.subheader(
    "💰 Payment Information"
)


if remaining > 0:

    st.warning(
        f"Outstanding amount: ₹{remaining:,.2f}"
    )

else:

    st.success(
        "✅ This sale is fully paid."
    )


# =========================================================
# EXCEL
# =========================================================

st.divider()

if st.button(
    "📊 Update Excel",
    use_container_width=True
):

    try:

        file_path = export_all_to_excel()

        st.success(
            f"Excel updated successfully: "
            f"{file_path.name}"
        )

    except Exception as e:

        st.error(
            f"Excel export failed: {e}"
        )


# =========================================================
# DASHBOARD
# =========================================================

if st.button(
    "🏠 Back to Dashboard",
    use_container_width=True
):

    st.switch_page(
        "app.py"
    )