import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Import AI module
from utils.ask_ai import ASK_AI

# Import snapshot storage helpers
from utils.storage import list_snapshots, load_snapshot, load_last_snapshot

st.set_page_config(layout="wide")

st.title("🏡 ARV & Comps Analyzer")
st.caption("Analyze ARV based on sold comparable properties (last 12 months, radius up to 0.7 miles).")

st.markdown("---")

# --------------------------------------------------
# 📂 LOAD SUBJECT PROPERTY FROM SNAPSHOT
# --------------------------------------------------
st.subheader("📂 Load Subject Property")

# Load snapshot list
snapshots = list_snapshots()

selected_snapshot = st.selectbox("📂 Load Property Snapshot", ["-- Select --"] + snapshots)

# Default empty values
subject_address = ""
subject_beds = 0
subject_baths = 0
subject_sqft = 0
subject_year = 0

if selected_snapshot != "-- Select --":
    snap = load_snapshot(selected_snapshot)

    # Correct field names from Property Lookup
    subject_address = snap.get("address", "")
    subject_beds = float(snap.get("beds", 0) or 0)
    subject_baths = float(snap.get("baths", 0) or 0)
    subject_sqft = float(snap.get("sqft", 0) or 0)
    subject_year = int(snap.get("year_built", 0) or 0)

    st.success(f"Loaded snapshot: {selected_snapshot}")

# --------------------------------------------------
# SHOW SUBJECT PROPERTY FIELDS
# --------------------------------------------------
st.subheader("🏠 Subject Property Details")

col1, col2 = st.columns(2)

with col1:
    subject_address = st.text_input("Property Address", value=subject_address)
    subject_beds = st.number_input("Beds", min_value=0.0, step=0.5, value=subject_beds)
    subject_baths = st.number_input("Baths", min_value=0.0, step=0.5, value=subject_baths)

with col2:
    subject_sqft = st.number_input("Living Area (sqft)", min_value=0.0, step=10.0, value=subject_sqft)
    subject_year = st.number_input("Year Built", min_value=1800, max_value=2100, step=1, value=subject_year)

st.markdown("---")

# --------------------------------------------------
# COMPARABLE SALES TABLE (MANUAL INPUT)
# --------------------------------------------------
st.subheader("🏘 Comparable Sales (Manual Entry)")

st.markdown("""
Enter sold comparable properties.
Recommended:
- Sold within 12 months  
- Within 0.7 miles  
- Data from Zillow, Redfin, Realtor, County, MLS, ATTOM, etc.
""")

default_data = pd.DataFrame({
    "Address": ["" for _ in range(5)],
    "Sale Date (YYYY-MM-DD)": ["" for _ in range(5)],
    "Sale Price": [0 for _ in range(5)],
    "Beds": [0.0 for _ in range(5)],
    "Baths": [0.0 for _ in range(5)],
    "Sqft": [0.0 for _ in range(5)],
    "Distance (miles)": [0.0 for _ in range(5)],
    "Renovated? (Yes/No)": ["" for _ in range(5)],
})

comps_df = st.data_editor(default_data, num_rows="dynamic", use_container_width=True, key="comps_editor")

st.markdown("---")

# --------------------------------------------------
# ARV CALCULATION
# --------------------------------------------------
st.subheader("📈 ARV Calculation")

if st.button("Calculate ARV"):
    df = comps_df.copy()

    # Convert values
    df["Sale Price"] = pd.to_numeric(df["Sale Price"], errors="coerce")
    df["Sqft"] = pd.to_numeric(df["Sqft"], errors="coerce")
    df["Distance (miles)"] = pd.to_numeric(df["Distance (miles)"], errors="coerce")
    df["Sale Date (YYYY-MM-DD)"] = pd.to_datetime(df["Sale Date (YYYY-MM-DD)"], errors="coerce")

    df = df.dropna(subset=["Sale Price", "Sqft"])

    if df.empty:
        st.error("No valid comps detected!")
    else:
        df["Price per Sqft"] = df["Sale Price"] / df["Sqft"]

        today = datetime.today()
        last_12_months = today - timedelta(days=365)

        df_recent = df[df["Sale Date (YYYY-MM-DD)"] >= last_12_months]
        df_recent_radius = df_recent[df_recent["Distance (miles)"] <= 0.7]

        filtered = df_recent_radius

        notes = []

        if len(filtered) < 3:
            notes.append("Less than 3 comps within 12 months + 0.7 miles.")
            filtered = df_recent

        if len(filtered) < 3:
            notes.append("Still less than 3 comps → using ALL comps.")
            filtered = df

        for n in notes:
            st.warning(n)

        if filtered.empty:
            st.error("No comps available after filtering.")
        else:
            median_ppsqft = filtered["Price per Sqft"].median()
            avg_ppsqft = filtered["Price per Sqft"].mean()
            min_ppsqft = filtered["Price per Sqft"].min()
            max_ppsqft = filtered["Price per Sqft"].max()

            # ARV results
            if subject_sqft > 0:
                arv_median = median_ppsqft * subject_sqft
                arv_avg = avg_ppsqft * subject_sqft
                arv_low = min_ppsqft * subject_sqft
                arv_high = max_ppsqft * subject_sqft
            else:
                arv_median = arv_avg = arv_low = arv_high = 0

            colA, colB, colC, colD = st.columns(4)
            colA.metric("Median $/sqft", f"${median_ppsqft:,.0f}")
            colB.metric("Avg $/sqft", f"${avg_ppsqft:,.0f}")
            colC.metric("Min $/sqft", f"${min_ppsqft:,.0f}")
            colD.metric("Max $/sqft", f"${max_ppsqft:,.0f}")

            st.subheader("🏁 ARV Estimates")
            st.metric("ARV (Median)", f"${arv_median:,.0f}")
            st.metric("ARV (Average)", f"${arv_avg:,.0f}")
            st.metric("ARV Low", f"${arv_low:,.0f}")
            st.metric("ARV High", f"${arv_high:,.0f}")

            st.subheader("📋 Comps Used")
            st.dataframe(filtered)
