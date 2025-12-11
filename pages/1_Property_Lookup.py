import streamlit as st
import pandas as pd

# Zillow auto-scraper
from utils.zillow_scraper import get_property_data

st.set_page_config(
    page_title="Property Lookup - Manual + Zillow Auto",
    page_icon="🏡",
    layout="wide"
)

st.title("🏡 Property Snapshot – Manual + Zillow Auto")
st.caption("Enter property data manually OR paste a Zillow URL for automatic fill.")

st.markdown("---")

# --------------------------------------------------
# BASIC INFO
# --------------------------------------------------

col_a, col_b = st.columns(2)

with col_a:
    address = st.text_input("Full Address")

with col_b:
    mls = st.text_input("MLS # (optional)")

# Zillow URL input
zillow_url = st.text_input("Zillow URL (optional)", placeholder="https://www.zillow.com/…")

# Default values BEFORE Zillow autofill
beds = 0.0
baths = 0.0
sqft = 0.0
lot_sqft = 0.0
year_built = 1970
list_price = 0.0

# --------------------------------------------------
# AUTO-FILL FROM ZILLOW
# --------------------------------------------------

if zillow_url:
    with st.spinner("Fetching Zillow data…"):
        data = get_property_data(zillow_url)

        if data.get("error"):
            st.error(f"Failed to fetch Zillow data: {data['error']}")

        else:
            # Apply Zillow data if available
            if data.get("address"): address = data["address"]
            if data.get("beds"): beds = float(data["beds"])
            if data.get("baths"): baths = float(data["baths"])
            if data.get("sqft"): sqft = float(data["sqft"])
            if data.get("lot_size"): lot_sqft = float(data["lot_size"])
            if data.get("year_built"): year_built = int(data["year_built"])
            if data.get("list_price"): list_price = float(data["list_price"])

            st.success("Zillow data imported successfully!")

# --------------------------------------------------
# MANUAL FIELDS (editable even after auto-fill)
# --------------------------------------------------

col1, col2, col3, col4 = st.columns(4)

with col1:
    beds = st.number_input("Beds", value=beds, min_value=0.0, step=0.5)

with col2:
    baths = st.number_input("Baths", value=baths, min_value=0.0, step=0.5)

with col3:
    sqft = st.number_input("Living Area (sqft)", value=sqft, min_value=0.0, step=10.0)

with col4:
    lot_sqft = st.number_input("Lot Size (sqft)", value=lot_sqft, min_value=0.0, step=100.0)

col5, col6 = st.columns(2)

with col5:
    year_built = st.number_input("Year Built", value=year_built, min_value=1800, max_value=2100, step=1)

with col6:
    property_type = st.selectbox(
        "Property Type",
        ["Single Family", "Duplex", "Triplex", "Fourplex", "Condo", "Townhouse", "Other"]
    )

st.markdown("---")

# --------------------------------------------------
# PRICE & RENT
# --------------------------------------------------

col7, col8, col9 = st.columns(3)

with col7:
    list_price = st.number_input("List Price ($)", value=list_price, min_value=0.0, step=1000.0)

with col8:
    rent_est = st.number_input("Estimated Rent ($/month)", min_value=0.0, step=50.0)

with col9:
    taxes_year = st.number_input("Annual Taxes ($)", min_value=0.0, step=100.0)

# Derived metrics
price_per_sqft = list_price / sqft if sqft > 0 else 0
rent_to_price = (rent_est * 12 / list_price * 100) if list_price > 0 and rent_est > 0 else 0

st.markdown("---")

# --------------------------------------------------
# SAVE SNAPSHOT
# --------------------------------------------------

from utils.storage import save_property_snapshot

if st.button("💾 Create Snapshot"):
    if not address:
        st.error("Please enter at least an address.")
    else:
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

        filename = save_property_snapshot(address.replace(" ", "_"), snapshot_data)
        st.success(f"Snapshot saved successfully! 📁 ({filename})")
