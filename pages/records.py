import streamlit as st

from database import (
    init_database,
    get_sales,
    get_sale_items,
    get_payment_history,
    mark_sale_paid,
    add_payment,
    cancel_sale
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
    page_title="Sales Records",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
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

st.title("📋 Sales Records")

st.caption(
    "View every transaction, payment and outstanding balance."
)


# =========================================================
# FILTER BAR
# =========================================================

st.subheader("🔎 Find Records")


col1, col2 = st.columns([1, 2])


with col1:

    period = st.selectbox(
        "Period",
        [
            "Today",
            "This Week",
            "This Month",
            "All Time"
        ]
    )


with col2:

    search = st.text_input(
        "Search",
        placeholder="Customer name / phone / Sale ID"
    )


# =========================================================
# QUICK CUSTOMER FILTER
# =========================================================

st.subheader("⚡ Quick Customer Filter")

if "record_customer_filter" not in st.session_state:
    st.session_state["record_customer_filter"] = "All Customers"

q1, q2, q3, q4 = st.columns(4)

with q1:
    if st.button(
        "👥 All Customers",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state["record_customer_filter"] == "All Customers"
            else "secondary"
        ),
    ):
        st.session_state["record_customer_filter"] = "All Customers"
        st.rerun()

with q2:
    if st.button(
        "👤 Raju",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state["record_customer_filter"] == "Raju"
            else "secondary"
        ),
    ):
        st.session_state["record_customer_filter"] = "Raju"
        st.rerun()

with q3:
    if st.button(
        "👤 Harvali",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state["record_customer_filter"] == "Harvali"
            else "secondary"
        ),
    ):
        st.session_state["record_customer_filter"] = "Harvali"
        st.rerun()

with q4:
    if st.button(
        "👤 Bhakt",
        use_container_width=True,
        type=(
            "primary"
            if st.session_state["record_customer_filter"] == "Bhakt"
            else "secondary"
        ),
    ):
        st.session_state["record_customer_filter"] = "Bhakt"
        st.rerun()


selected_customer_filter = st.session_state["record_customer_filter"]

if selected_customer_filter != "All Customers":
    st.caption(
        f"Showing records for **{selected_customer_filter}**"
    )


# =========================================================
# LOAD SALES
# =========================================================

sales = get_sales(
    period=period,
    search=search
)

if selected_customer_filter != "All Customers":
    sales = [
        sale
        for sale in sales
        if str(sale["customer_name"]).strip().lower()
        == selected_customer_filter.lower()
    ]


# =========================================================
# SUMMARY
# =========================================================

total_sales = sum(
    sale["total"]
    for sale in sales
)

total_received = sum(
    sale["received"]
    for sale in sales
)

total_pending = sum(
    sale["remaining"]
    for sale in sales
)


st.subheader(
    "Overview"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "💰 Total Sales",
        f"₹{total_sales:,.2f}"
    )


with col2:

    st.metric(
        "✅ Received",
        f"₹{total_received:,.2f}"
    )


with col3:

    st.metric(
        "⚠️ Outstanding",
        f"₹{total_pending:,.2f}"
    )


with col4:

    st.metric(
        "🧾 Transactions",
        len(sales)
    )


st.divider()


# =========================================================
# STATUS FILTER
# =========================================================

status_filter = st.radio(
    "Payment Status",
    [
        "All",
        "Paid",
        "Partially Paid",
        "Unpaid"
    ],
    horizontal=True
)


if status_filter != "All":

    sales = [
        sale
        for sale in sales
        if sale["status"] == status_filter
    ]


# =========================================================
# TRANSACTION LIST
# =========================================================

st.subheader(
    f"Transactions ({len(sales)})"
)


if not sales:

    st.info(
        "No transactions found for the selected filters."
    )

else:

    for sale in sales:

        # -------------------------------------------------
        # STATUS
        # -------------------------------------------------

        if sale["status"] == "Paid":

            status_icon = "✅"

        elif sale["status"] == "Partially Paid":

            status_icon = "🟡"

        else:

            status_icon = "🔴"


        # -------------------------------------------------
        # TRANSACTION HEADER
        # -------------------------------------------------

        sale_header = (
            f"{status_icon}  "
            f"Sale #{sale['id']}  |  "
            f"{sale['customer_name']}  |  "
            f"₹{sale['total']:,.2f}  |  "
            f"{sale['status']}"
        )


        with st.expander(
            sale_header
        ):

            # =============================================
            # TOP SUMMARY
            # =============================================

            col1, col2, col3, col4 = st.columns(4)


            with col1:

                st.metric(
                    "Sale",
                    f"#{sale['id']}"
                )


            with col2:

                st.metric(
                    "Total",
                    f"₹{sale['total']:,.2f}"
                )


            with col3:

                st.metric(
                    "Received",
                    f"₹{sale['received']:,.2f}"
                )


            with col4:

                st.metric(
                    "Remaining",
                    f"₹{sale['remaining']:,.2f}"
                )


            st.divider()


            # =============================================
            # CUSTOMER INFO
            # =============================================

            st.write(
                "### 👤 Customer"
            )


            col1, col2 = st.columns(2)


            with col1:

                st.write(
                    f"**Name:** "
                    f"{sale['customer_name']}"
                )


            with col2:

                st.write(
                    f"**Phone:** "
                    f"{sale['phone'] or 'Not provided'}"
                )


            st.write(
                f"🕐 **Sale Date & Time:** "
                f"{sale['created_at']}"
            )


            st.write(
                f"💳 **Payment Status:** "
                f"{status_icon} {sale['status']}"
            )


            st.divider()


            # =============================================
            # ITEMS
            # =============================================

            st.write(
                "### 🛒 Items"
            )


            items = get_sale_items(
                sale["id"]
            )


            if items:

                for item in items:

                    col1, col2, col3, col4 = st.columns(
                        [2.5, 1, 1, 1]
                    )


                    with col1:

                        st.write(
                            f"**{item['name']}**"
                        )


                    with col2:

                        st.write(
                            f"Qty: {item['quantity']}"
                        )


                    with col3:

                        st.write(
                            f"₹{float(item['price']):,.2f}"
                        )


                    with col4:

                        st.write(
                            f"₹{float(item['subtotal']):,.2f}"
                        )

            else:

                st.info(
                    "No items recorded."
                )


            st.divider()


            # =============================================
            # PAYMENT SECTION
            # =============================================

            st.write(
                "### 💰 Payment Management"
            )


            if sale["remaining"] > 0:

                st.warning(
                    f"₹{sale['remaining']:,.2f} "
                    f"still needs to be collected."
                )


                payment_method = st.radio(
                    "Payment Method",
                    [
                        "Cash",
                        "UPI",
                        "Other"
                    ],
                    horizontal=True,
                    key=f"method_{sale['id']}"
                )


                # -----------------------------------------
                # MARK FULLY PAID
                # -----------------------------------------

                if st.button(
                    f"✅ Mark as Paid — "
                    f"₹{sale['remaining']:,.2f}",
                    key=f"mark_paid_{sale['id']}",
                    use_container_width=True,
                    type="primary"
                ):

                    try:

                        amount = mark_sale_paid(
                            sale["id"],
                            payment_method
                        )


                        try:

                            export_all_to_excel()

                        except Exception:

                            pass


                        st.success(
                            f"₹{amount:,.2f} payment recorded."
                        )

                        st.success(
                            "✅ Sale is now fully paid."
                        )

                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"Payment failed: {e}"
                        )


                # -----------------------------------------
                # PARTIAL PAYMENT
                # -----------------------------------------

                st.write(
                    "Or record a partial payment"
                )


                col1, col2 = st.columns(2)


                with col1:

                    partial_amount = st.number_input(
                        "Amount ₹",
                        min_value=0.0,
                        max_value=float(
                            sale["remaining"]
                        ),
                        step=1.0,
                        key=f"partial_amount_{sale['id']}"
                    )


                with col2:

                    partial_method = st.selectbox(
                        "Payment Method",
                        [
                            "Cash",
                            "UPI",
                            "Other"
                        ],
                        key=f"partial_method_{sale['id']}"
                    )


                if st.button(
                    "➕ Add Partial Payment",
                    key=f"partial_payment_{sale['id']}",
                    use_container_width=True
                ):

                    try:

                        add_payment(
                            sale_id=sale["id"],
                            amount=partial_amount,
                            method=partial_method,
                            note="Partial payment"
                        )


                        try:

                            export_all_to_excel()

                        except Exception:

                            pass


                        st.success(
                            "✅ Payment added successfully."
                        )

                        st.rerun()


                    except Exception as e:

                        st.error(
                            str(e)
                        )


            else:

                st.success(
                    "✅ This sale is fully paid."
                )


            st.divider()


            # =============================================
            # PAYMENT HISTORY
            # =============================================

            payments = get_payment_history(
                sale["id"]
            )


            st.write(
                "### 📜 Payment History"
            )


            if payments:

                for payment in payments:

                    st.write(
                        f"**₹{payment['amount']:,.2f}**  |  "
                        f"{payment['method']}  |  "
                        f"{payment['created_at']}  |  "
                        f"{payment['note'] or ''}"
                    )

            else:

                st.caption(
                    "No payment history available."
                )


            st.divider()


            # =============================================
            # SALE MANAGEMENT
            # =============================================

            st.write(
                "### ⚙️ Sale Management"
            )


            confirm_cancel = st.checkbox(
                "I understand this sale will be cancelled.",
                key=f"confirm_cancel_{sale['id']}"
            )


            if confirm_cancel:

                if st.button(
                    "❌ Cancel Sale",
                    key=f"cancel_sale_{sale['id']}",
                    use_container_width=True
                ):

                    try:

                        cancel_sale(
                            sale["id"]
                        )

                        try:

                            export_all_to_excel()

                        except Exception:

                            pass


                        st.success(
                            f"Sale #{sale['id']} cancelled."
                        )

                        st.rerun()


                    except Exception as e:

                        st.error(
                            f"Could not cancel sale: {e}"
                        )


# =========================================================
# EXCEL
# =========================================================

st.divider()

st.subheader(
    "📊 Excel"
)


if st.button(
    "Update Excel Report",
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