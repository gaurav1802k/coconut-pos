
import streamlit as st


def apply_theme():
    st.markdown(
        """
        <style>
        :root {
            --bg: #0b0f0d;
            --surface: #141a16;
            --surface-2: #181f1a;
            --surface-3: #1d2720;
            --text: #f2f6f3;
            --text-soft: #c9d2cc;
            --muted: #8c9991;
            --line: #29342d;
            --line-strong: #38483d;
            --green: #29b968;
            --green-dark: #dff7e7;
        }

        /* APP */
        .stApp {
            background: #0b0f0d !important;
            color: var(--text) !important;
        }

        .main, [data-testid="stAppViewContainer"] {
            background: #0b0f0d !important;
        }

        .block-container {
            max-width: 1140px !important;
            padding: .8rem 1.2rem 3rem !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
        }

        /* SIDEBAR */
        section[data-testid="stSidebar"] {
            background: #101512 !important;
            border-right: 1px solid #202a23 !important;
        }

        section[data-testid="stSidebar"] > div {
            padding: .8rem .7rem 1.5rem !important;
        }

        [data-testid="stSidebarNav"] {
            display: none !important;
        }

        .brand-card {
            background: #151c17;
            border: 1px solid #2a352e;
            border-radius: 18px;
            padding: 16px 15px;
            margin-bottom: 14px;
        }

        .brand-title {
            color: #f2f7f3;
            font-size: 1.1rem;
            font-weight: 900;
        }

        .brand-sub {
            color: #829087;
            font-size: .76rem;
            margin-top: 5px;
        }

        section[data-testid="stSidebar"] .stButton > button {
            background: transparent !important;
            color: #aeb9b2 !important;
            border: 1px solid transparent !important;
            border-radius: 11px !important;
            min-height: 40px !important;
            box-shadow: none !important;
            text-align: left !important;
            justify-content: flex-start !important;
            font-weight: 750 !important;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #1a221d !important;
            border-color: #2b382f !important;
            color: #f1f6f2 !important;
        }

        /* TYPE */
        h1, h2, h3, h4 {
            color: #f2f6f3 !important;
        }

        h1 {
            font-size: clamp(2rem, 4vw, 3rem) !important;
            font-weight: 900 !important;
            letter-spacing: -.7px !important;
            line-height: 1.02 !important;
        }

        h2 {
            font-size: 1.3rem !important;
            font-weight: 850 !important;
        }

        p, label, .stCaption {
            color: var(--muted) !important;
        }

        /* HERO */
        .hero {
            background: #151c17 !important;
            border: 1px solid #2b372f !important;
            border-radius: 22px !important;
            padding: 22px 24px !important;
            box-shadow: 0 18px 42px rgba(0,0,0,.20) !important;
        }

        .eyebrow {
            color: #829087 !important;
            font-size: .68rem !important;
            font-weight: 850 !important;
            letter-spacing: .14em !important;
            text-transform: uppercase !important;
        }

        .hero-sub {
            color: #939e97 !important;
            font-size: .9rem !important;
            margin-top: 7px !important;
        }

        .time-card {
            background: #151c17 !important;
            border: 1px solid #2b372f !important;
            border-radius: 19px !important;
            padding: 16px 17px !important;
            box-shadow: 0 18px 42px rgba(0,0,0,.16) !important;
        }

        .time-label {
            color: #7f8c84 !important;
            font-size: .72rem !important;
            font-weight: 800 !important;
        }

        .time-value {
            color: #f2f6f3 !important;
            font-size: 1.5rem !important;
            font-weight: 900 !important;
            margin-top: 4px !important;
        }

        /* BIG NEW ENTRY */
        .entry-card {
            background: #16291d !important;
            border: 1px solid #316542 !important;
            border-radius: 19px !important;
            padding: 16px 18px 6px !important;
            margin-top: 5px !important;
        }

        .entry-title {
            color: #eef8f1 !important;
            font-size: 1.22rem !important;
            font-weight: 900 !important;
        }

        .entry-sub {
            color: #a0b1a5 !important;
            font-size: .8rem !important;
            margin-top: 4px !important;
        }

        /* Exact next button after entry card */
        div:has(> .entry-card) + div[data-testid="stButton"] > button {
            background: #29b968 !important;
            color: #ffffff !important;
            border: none !important;
            min-height: 68px !important;
            border-radius: 15px !important;
            font-size: 1rem !important;
            font-weight: 900 !important;
            letter-spacing: .04em !important;
            box-shadow: 0 12px 27px rgba(41,185,104,.18) !important;
        }

        div:has(> .entry-card) + div[data-testid="stButton"] > button:hover {
            background: #39c979 !important;
        }

        /* INPUTS */
        div[data-testid="stTextInput"] input,
        div[data-testid="stNumberInput"] input,
        textarea,
        div[data-baseweb="input"] input,
        div[data-baseweb="base-input"] input {
            background: transparent !important;
            color: #eef6f0 !important;
            -webkit-text-fill-color: #eef6f0 !important;
            border: 0 !important;
            outline: none !important;
            box-shadow: none !important;
        }

        div[data-baseweb="input"] > div,
        div[data-baseweb="base-input"] > div,
        div[data-baseweb="select"] > div {
            background: #151b17 !important;
            color: #eef6f0 !important;
            border: 1px solid #303c34 !important;
            border-radius: 12px !important;
            box-shadow: none !important;
            outline: none !important;
        }

        div[data-baseweb="input"] > div:focus-within,
        div[data-baseweb="select"] > div:focus-within {
            border-color: #4f6958 !important;
            box-shadow: 0 0 0 1px rgba(41,185,104,.08) !important;
        }

        div[data-baseweb="select"] span,
        div[data-baseweb="select"] input {
            color: #eef6f0 !important;
            -webkit-text-fill-color: #eef6f0 !important;
        }

        input::placeholder, textarea::placeholder {
            color: #67736b !important;
            -webkit-text-fill-color: #67736b !important;
            opacity: 1 !important;
        }

        /* DROPDOWN POPUP */
        div[data-baseweb="popover"],
        ul[role="listbox"],
        li[role="option"] {
            background: #171e19 !important;
            color: #eef6f0 !important;
        }

        li[role="option"]:hover,
        li[role="option"][aria-selected="true"] {
            background: #203028 !important;
            color: #ffffff !important;
        }

        /* BUTTONS */
        .stButton > button {
            min-height: 44px !important;
            border-radius: 12px !important;
            border: 1px solid #2b382f !important;
            background: #151c17 !important;
            color: #dce7df !important;
            font-weight: 800 !important;
            box-shadow: 0 5px 14px rgba(0,0,0,.10) !important;
        }

        .stButton > button:hover {
            background: #1c251f !important;
            color: #ffffff !important;
            border-color: #48604f !important;
        }

        /* METRICS */
        .metric-wrap {
            background: #151c17 !important;
            border: 1px solid #29362e !important;
            border-radius: 17px !important;
            padding: 14px 16px !important;
            min-height: 86px !important;
            box-shadow: 0 8px 21px rgba(0,0,0,.12) !important;
        }

        .metric-label {
            color: #849189 !important;
            font-size: .72rem !important;
            font-weight: 800 !important;
        }

        .metric-value {
            color: #f1f6f2 !important;
            font-size: 1.45rem !important;
            font-weight: 900 !important;
            margin-top: 6px !important;
        }

        /* OTHER */
        div[data-testid="stMetric"],
        div[data-testid="stExpander"],
        div[data-testid="stDataFrame"] {
            background: #151c17 !important;
            border-color: #29362e !important;
        }

        div[data-testid="stExpander"] {
            border-radius: 14px !important;
            box-shadow: none !important;
        }

        div[data-testid="stDataFrame"] {
            border-radius: 14px !important;
            overflow: hidden !important;
        }

        div[data-testid="stAlert"] {
            border-radius: 12px !important;
        }

        hr {
            border-color: #253129 !important;
        }

        footer, #MainMenu {
            visibility: hidden !important;
        }

        @media (max-width: 700px) {
            .block-container {
                padding: .65rem .7rem 2.2rem !important;
            }

            .hero {
                padding: 18px !important;
                border-radius: 19px !important;
            }

            .entry-card {
                padding: 15px !important;
                border-radius: 18px !important;
            }

            div:has(> .entry-card) + div[data-testid="stButton"] > button {
                min-height: 64px !important;
            }

            .metric-wrap {
                min-height: 82px !important;
                padding: 12px 13px !important;
            }

            .metric-value {
                font-size: 1.25rem !important;
            }

            .stButton > button {
                min-height: 48px !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def build_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div class="brand-card">
                <div class="brand-title">🥥 Coconut Business</div>
                <div class="brand-sub">Sales · Customers · Payments</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("Dashboard", use_container_width=True):
            st.switch_page("app.py")
        if st.button("New Sale", use_container_width=True):
            st.switch_page("pages/new_sale.py")
        if st.button("Sales Records", use_container_width=True):
            st.switch_page("pages/records.py")
        if st.button("Edit Sale", use_container_width=True):
            st.switch_page("pages/edit_sale.py")
        if st.button("Products", use_container_width=True):
            st.switch_page("pages/products.py")

        st.divider()
        st.caption("DATA")
        st.caption("SQLite Database")
        st.caption("Excel Reporting")
        st.caption("Automatic Backup")
