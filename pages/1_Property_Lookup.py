mport streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Property Lookup – Manual",
    page_icon="🏠",
    layout="wide"
)

st.title("🏠 Property Snapshot — Manual Entry (100% Reliable)")
st.caption("You grab the data from Zillow / Redfin / Realtor, the app organizes & analyzes it.")

st.markdown("---")

# -----------------------------
# BASIC INFO
# -----------------------------
col_a, col_b = st.columns(2)
with col_a:
    address = st.text_input("Full Address")
with col_b:
    mls = st.text_input("MLS # (optional)")

col1, col2, col3, col4 = st.columns(4)
with col1:
    beds = st.number_input("Beds", min_value=0.0, step=0.5)
with col2:
    baths = st.number_input("Baths", min_value=0.0, step=0.5)
with col3:
    sqft = st.number_input("Living Area (sqft)", min_value=0.0, step=10.0)
with col4:
   lot_size = st.number_input("Lot Size (sqft)", min_value=0.0, step=100.0)

col5, col6 = st.columns(2)
with col5:
    year_built = st.number_input("Year Built", min_value=1800, max_value=2100, step=1, value=1970)
with col6:
    property_type = st.selectbox(
        "Property Type",
        ["Single Family", "Duplex", "Triplex", "Fourplex", "Condo", "Townhouse", "Other"]
    )

st.markdown("---")

# -----------------------------
# PRICE & RENT
# -----------------------------
col7, col8, col9 = st.columns(3)
with col7:
    list_price = st.number_input("List Price ($)", min_value=0.0, step=1000.0)
with col8:
    rent_est = st.number_input("Estimated Rent ($/month)", min_value=0.0, step=50.0)
with col9:
    taxes_year = st.number_input("Annual Taxes ($)", min_value=0.0, step=100.0)

# Derived metrics
price_per_sqft = list_price / sqft if list_price > 0 and sqft > 0 else 0
price_per_unit = list_price  # for future multi-family
rent_to_price = (rent_est * 12 / list_price * 100) if list_price > 0 and rent_est > 0 else 0

st.markdown("---")

# -------------------------------------------------
# Create Snapshot (Save Property Data)
# -------------------------------------------------

# -------------------------------------------------
# Create Snapshot (Save Property Data)
# -------------------------------------------------

if st.button("📌 Create Snapshot"):
    if not address:
        st.error("Please enter at least an address.")
    else:
        from utils.storage import save_property_snapshot

        # Prepare data to save
        snapshot_data = {
            "address": address,
            "mls": mls,
            "type": property_type,
            "beds": beds,
            "baths": baths,
            "sqft": sqft,
            "lot_size": lot_sqft,
            "year_built": year_built,
            "list_price": list_price,
            "rent_est": rent_est,
            "taxes_year": taxes_year,
            "price_per_sqft": price_per_sqft,
            "rent_to_price": rent_to_price,
        }

        # Save snapshot using sanitized address as file name
        filename = save_property_snapshot(address.replace(" ", "_"), snapshot_data)
        st.success(f"Snapshot saved successfully! 📁 ({filename})")
