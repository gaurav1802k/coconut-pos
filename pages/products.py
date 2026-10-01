import streamlit as st

from database import (
    init_database,
    get_products,
    add_product,
    update_product,
    set_product_active
)

from theme import (
    apply_theme,
    build_sidebar
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Products",
    page_icon="📦",
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

st.title("📦 Products")

st.caption(
    "Manage your item catalogue, prices and availability."
)


st.divider()


# =========================================================
# ADD NEW PRODUCT
# =========================================================

st.subheader("➕ Add New Item")

st.caption(
    "Add a new product to your regular sales list."
)


col1, col2, col3 = st.columns(
    [2.5, 1, 1]
)


with col1:

    new_name = st.text_input(
        "Item Name",
        placeholder="Example: Coconut"
    )


with col2:

    new_price = st.number_input(
        "Price ₹",
        min_value=0.0,
        step=1.0,
        value=0.0
    )


with col3:

    st.write("")

    if st.button(
        "➕ Add Item",
        use_container_width=True,
        type="primary"
    ):

        try:

            add_product(
                new_name,
                new_price
            )

            st.success(
                f"✅ {new_name} added successfully."
            )

            st.rerun()

        except Exception as e:

            st.error(
                str(e)
            )


st.divider()


# =========================================================
# PRODUCT LIST
# =========================================================

st.subheader("📋 Product Catalogue")

st.caption(
    "Current item prices and availability."
)


products = get_products(
    active_only=False
)


if not products:

    st.info(
        "No products available."
    )

else:

    # -----------------------------------------------------
    # SUMMARY
    # -----------------------------------------------------

    total_products = len(products)

    active_products = sum(
        1
        for product in products
        if product["active"]
    )

    inactive_products = (
        total_products
        - active_products
    )


    col1, col2, col3 = st.columns(3)


    with col1:

        st.metric(
            "📦 Total Items",
            total_products
        )


    with col2:

        st.metric(
            "✅ Active",
            active_products
        )


    with col3:

        st.metric(
            "⏸️ Inactive",
            inactive_products
        )


    st.divider()


    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    search = st.text_input(
        "🔎 Search Products",
        placeholder="Search item name"
    )


    if search.strip():

        products_to_show = [
            product
            for product in products
            if search.lower()
            in product["name"].lower()
        ]

    else:

        products_to_show = products


    # -----------------------------------------------------
    # PRODUCTS
    # -----------------------------------------------------

    if not products_to_show:

        st.info(
            "No product matches your search."
        )

    else:

        for product in products_to_show:

            product_id = product["id"]
            product_name = product["name"]
            product_price = float(
                product["price"]
            )
            is_active = bool(
                product["active"]
            )


            # =============================================
            # PRODUCT CONTAINER
            # =============================================

            with st.container(
                border=True
            ):

                # -----------------------------------------
                # HEADER
                # -----------------------------------------

                col1, col2 = st.columns(
                    [3, 1]
                )


                with col1:

                    st.markdown(
                        f"### 🥥 {product_name}"
                    )

                    if is_active:

                        st.success(
                            "● Active"
                        )

                    else:

                        st.warning(
                            "● Inactive"
                        )


                with col2:

                    st.metric(
                        "Current Price",
                        f"₹{product_price:,.2f}"
                    )


                st.divider()


                # -----------------------------------------
                # EDIT PRODUCT
                # -----------------------------------------

                col1, col2, col3 = st.columns(
                    [2.5, 1.2, 1.2]
                )


                with col1:

                    edited_name = st.text_input(
                        "Item Name",
                        value=product_name,
                        key=f"name_{product_id}"
                    )


                with col2:

                    edited_price = st.number_input(
                        "Price ₹",
                        min_value=0.0,
                        value=product_price,
                        step=1.0,
                        key=f"price_{product_id}"
                    )


                with col3:

                    st.write("")

                    if st.button(
                        "💾 Save Changes",
                        key=f"save_{product_id}",
                        use_container_width=True
                    ):

                        if not edited_name.strip():

                            st.error(
                                "Item name cannot be empty."
                            )

                        elif edited_price <= 0:

                            st.error(
                                "Price must be greater than ₹0."
                            )

                        else:

                            try:

                                update_product(
                                    product_id,
                                    edited_name,
                                    edited_price
                                )

                                st.success(
                                    "✅ Product updated."
                                )

                                st.rerun()

                            except Exception as e:

                                st.error(
                                    str(e)
                                )


                # -----------------------------------------
                # AVAILABILITY
                # -----------------------------------------

                st.write("")

                if is_active:

                    if st.button(
                        "⏸️ Deactivate Product",
                        key=f"deactivate_{product_id}",
                        use_container_width=True
                    ):

                        set_product_active(
                            product_id,
                            False
                        )

                        st.success(
                            f"{product_name} deactivated."
                        )

                        st.rerun()

                else:

                    if st.button(
                        "▶️ Reactivate Product",
                        key=f"activate_{product_id}",
                        use_container_width=True
                    ):

                        set_product_active(
                            product_id,
                            True
                        )

                        st.success(
                            f"{product_name} is active again."
                        )

                        st.rerun()


st.divider()


# =========================================================
# DEFAULT PRODUCTS
# =========================================================

st.subheader("🥥 Current Regular Items")

st.caption(
    "Your standard items used during sales."
)


regular_items = [
    ("Coconut", 20),
    ("Oti Saman", 2),
    ("Tel", 5),
    ("Sadi", 5)
]


for item_name, standard_price in regular_items:

    matching_product = next(
        (
            p
            for p in products
            if p["name"].lower()
            == item_name.lower()
        ),
        None
    )


    if matching_product:

        col1, col2, col3 = st.columns(
            [2, 1, 1]
        )


        with col1:

            st.write(
                f"🥥 **{matching_product['name']}**"
            )


        with col2:

            st.write(
                f"₹{float(matching_product['price']):,.2f}"
            )


        with col3:

            if matching_product["active"]:

                st.success(
                    "Active"
                )

            else:

                st.warning(
                    "Inactive"
                )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "🥥 Coconut Business Manager • Product Register"
)