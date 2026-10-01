
import streamlit as st
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

from database import init_database, get_sales, get_sale_items
from excel_export import export_all_to_excel

try:
    from database import reset_all_data
except ImportError:
    reset_all_data = None

try:
    from excel_export import reset_excel_workbook
except ImportError:
    reset_excel_workbook = None

from theme import apply_theme, build_sidebar


st.set_page_config(
    page_title="Coconut Business",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_database()
apply_theme()
build_sidebar()

now = datetime.now(ZoneInfo("Asia/Kolkata"))
today_text = now.strftime("%A, %d %B %Y")
time_text = now.strftime("%I:%M %p")

# ---------------------------------------------------------
# HERO
# ---------------------------------------------------------
left, right = st.columns([3.0, 1], vertical_alignment="center")

with left:
    st.markdown(
        f"""
        <div class="hero">
            <div class="eyebrow">Good morning · {today_text}</div>
            <h1>Coconut Business</h1>
            <div class="hero-sub">Sales, customers and payments — simple and organized.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with right:
    st.markdown(
        f"""
        <div class="time-card">
            <div class="time-label">Current time</div>
            <div class="time-value">{time_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.write("")

# ---------------------------------------------------------
# BIG NEW ENTRY
# ---------------------------------------------------------
st.markdown(
    """
    <div class="entry-card">
        <div class="entry-title">New Entry</div>
        <div class="entry-sub">Tap here to record a customer sale.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.button("NEW ENTRY", use_container_width=True, type="primary"):
    st.switch_page("pages/new_sale.py")

st.write("")

# ---------------------------------------------------------
# FILTERS
# ---------------------------------------------------------
st.markdown('<div class="section-title">Sales overview</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Choose a period or search for a transaction.</div>',
    unsafe_allow_html=True,
)

f1, f2 = st.columns([1, 2])

with f1:
    period = st.selectbox(
        "View period",
        ["Today", "This Week", "This Month", "All Time"],
        label_visibility="collapsed",
    )

with f2:
    search = st.text_input(
        "Search",
        placeholder="Customer, phone number or Sale ID",
        label_visibility="collapsed",
    )

sales = get_sales(period=period, search=search)

total_sales = sum(float(s["total"]) for s in sales)
total_received = sum(float(s["received"]) for s in sales)
total_pending = sum(float(s["remaining"]) for s in sales)

st.write("")

# ---------------------------------------------------------
# SNAPSHOT
# ---------------------------------------------------------
st.markdown('<div class="section-title">Today\'s snapshot</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">A clean overview of the selected period.</div>',
    unsafe_allow_html=True,
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        f'<div class="metric-wrap green"><div class="metric-label">Sales</div><div class="metric-value">₹{total_sales:,.0f}</div></div>',
        unsafe_allow_html=True,
    )

with m2:
    st.markdown(
        f'<div class="metric-wrap green"><div class="metric-label">Received</div><div class="metric-value">₹{total_received:,.0f}</div></div>',
        unsafe_allow_html=True,
    )

with m3:
    st.markdown(
        f'<div class="metric-wrap amber"><div class="metric-label">Pending</div><div class="metric-value">₹{total_pending:,.0f}</div></div>',
        unsafe_allow_html=True,
    )

with m4:
    st.markdown(
        f'<div class="metric-wrap blue"><div class="metric-label">Orders</div><div class="metric-value">{len(sales)}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# ---------------------------------------------------------
# QUICK CUSTOMERS
# ---------------------------------------------------------
st.markdown('<div class="section-title">Quick customers</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Your three regular customers, one tap away.</div>',
    unsafe_allow_html=True,
)

q1, q2, q3 = st.columns(3)

with q1:
    if st.button("Raju", use_container_width=True):
        st.session_state["quick_customer"] = "Raju"
        st.switch_page("pages/records.py")

with q2:
    if st.button("Harvali", use_container_width=True):
        st.session_state["quick_customer"] = "Harvali"
        st.switch_page("pages/records.py")

with q3:
    if st.button("Bhakt", use_container_width=True):
        st.session_state["quick_customer"] = "Bhakt"
        st.switch_page("pages/records.py")

st.write("")

# ---------------------------------------------------------
# QUICK ACTIONS
# ---------------------------------------------------------
st.markdown('<div class="section-title">Quick actions</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Common daily tasks.</div>',
    unsafe_allow_html=True,
)

a1, a2, a3 = st.columns(3)

with a1:
    if st.button("New Sale", use_container_width=True, type="primary"):
        st.switch_page("pages/new_sale.py")

with a2:
    if st.button("Sales Records", use_container_width=True):
        st.switch_page("pages/records.py")

with a3:
    if st.button("Update Excel", use_container_width=True):
        try:
            path = export_all_to_excel()
            st.success(f"Excel updated: {path.name}")
        except Exception as e:
            st.error(f"Excel export failed: {e}")

st.write("")

# ---------------------------------------------------------
# CUSTOMER OVERVIEW
# ---------------------------------------------------------
st.markdown('<div class="section-title">Customer overview</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Purchase, received and outstanding amounts.</div>',
    unsafe_allow_html=True,
)

all_sales = get_sales(period="All Time")

customer_data = defaultdict(
    lambda: {
        "Customer": "",
        "Phone": "",
        "Orders": 0,
        "Total Purchase": 0.0,
        "Received": 0.0,
        "Outstanding": 0.0,
    }
)

for sale in all_sales:
    cid = sale["customer_id"]
    customer_data[cid]["Customer"] = sale["customer_name"]
    customer_data[cid]["Phone"] = sale["phone"]
    customer_data[cid]["Orders"] += 1
    customer_data[cid]["Total Purchase"] += float(sale["total"])
    customer_data[cid]["Received"] += float(sale["received"])
    customer_data[cid]["Outstanding"] += float(sale["remaining"])

customer_rows = list(customer_data.values())

if customer_rows:
    customer_rows.sort(key=lambda x: x["Total Purchase"], reverse=True)

    st.dataframe(
        customer_rows,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Customer": st.column_config.TextColumn("Customer"),
            "Phone": st.column_config.TextColumn("Phone"),
            "Orders": st.column_config.NumberColumn("Orders"),
            "Total Purchase": st.column_config.NumberColumn(
                "Total Purchase", format="₹%.2f"
            ),
            "Received": st.column_config.NumberColumn(
                "Received", format="₹%.2f"
            ),
            "Outstanding": st.column_config.NumberColumn(
                "Outstanding", format="₹%.2f"
            ),
        },
    )
else:
    st.info("No customer records yet.")

st.write("")

# ---------------------------------------------------------
# RECENT TRANSACTIONS
# ---------------------------------------------------------
st.markdown('<div class="section-title">Recent transactions</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-sub">Latest activity for the selected period.</div>',
    unsafe_allow_html=True,
)

if sales:
    for sale in sales[:8]:
        title = (
            f"Sale #{sale['id']}  ·  {sale['customer_name']}  ·  "
            f"₹{sale['total']:,.0f}  ·  {sale['status']}"
        )

        with st.expander(title):
            c1, c2, c3 = st.columns(3)

            with c1:
                st.write("Customer")
                st.write(sale["customer_name"])
                st.caption(sale["phone"] or "No phone")

            with c2:
                st.write("Payment")
                st.write(f"Total: ₹{sale['total']:,.2f}")
                st.write(f"Received: ₹{sale['received']:,.2f}")

            with c3:
                st.write("Balance")
                st.write(f"Remaining: ₹{sale['remaining']:,.2f}")
                st.write(f"Status: {sale['status']}")

            st.divider()
            st.write("Items")

            for item in get_sale_items(sale["id"]):
                st.write(
                    f"{item['name']} × {item['quantity']} = "
                    f"₹{float(item['subtotal']):,.2f}"
                )
else:
    st.info("No transactions found.")

# ---------------------------------------------------------
# DANGER ZONE
# ---------------------------------------------------------
if reset_all_data is not None and reset_excel_workbook is not None:
    st.write("")

    with st.expander("Danger zone"):
        st.warning("This permanently deletes sales, payments and customers.")

        confirm = st.checkbox(
            "I understand that this will permanently delete business data.",
            key="dashboard_reset_confirm",
        )

        if st.button(
            "Reset all data",
            use_container_width=True,
            disabled=not confirm,
        ):
            try:
                reset_excel_workbook()
                reset_all_data()
                st.success("Everything reset. Next sale will be Sale ID 1.")
                st.rerun()
            except PermissionError:
                st.error("Close coconut_sales.xlsx before resetting.")
            except Exception as e:
                st.error(f"Reset failed: {e}")

st.caption("Coconut Business Manager · SQLite · Excel")
