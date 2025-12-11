import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Import AI helper
from utils.ask_ai import ASK_AI

# Import snapshot storage helpers
from utils.storage import list_snapshots, load_snapshot, load_last_snapshot

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------
st.set_page_config(layout="wide")

st.title("🏡 ARV & Comps Analyzer")
st.caption("Analyze ARV based on sold comparable properties (last 12 months, radius up to 0.7 miles).")

st.markdown("---")

# --------------------------------------------------
# 🔹 LOAD SUBJECT PROPERTY FROM SNAPSHOT
# --------------------------------------------------
st.subheader("📂 Load Subject Property Snapshot")

snapshots = list_snapshots()

selected_snapshot = st.selectbox(
    "📂 Choose Property Snapshot",
    ["-- Select --"] + snapshots
)

# Default values
subject_address = ""
subject_beds = 0
subject_baths = 0
subject_sqft = 0
subject_year = 0

if selected_snapshot != "-- Select --":
    data = load_snapshot(selected_snapshot)

    subject_address = data.get("address", "")
    subject_beds = data.get("beds", 0)
    subject_baths = data.get("baths", 0)
    subject_sqft = data.get("sqft", 0)
    subject_year = data.get("year_built", 0)

    st.success(f"Loaded snapshot: {selected_snapshot}")

else:
    st.info("Select a snapshot to auto-fill subject property details.")

st.markdown("---")

# --------------------------------------------------
# 🔹 SUBJECT PROPERTY MANUAL EDIT
# --------------------------------------------------
st.subheader("🏠 Subject Property Details")

col1, col2 = st.columns(2)

with col1:
    subject_address = st.text_input("Property Address", value=subject_address)
    subject_beds = st.number_input("Beds", min_value=0.0, step=0.5, value=float(subject_beds))
    subject_baths = st.number_input("Baths", min_value=0.0, step=0.5, value=float(subject_baths))

with col2:
    subject_sqft = st.number_input("Living Area (sqft)", min_value=0.0, step=10.0, value=float(subject_sqft))
    subject_year = st.number_input("Year Built", min_value=1800, max_value=2100, step=1, value=int(subject_year))

st.markdown("---")

# --------------------------------------------------
# 🔹 MANUAL COMPARABLE SALES INPUT
# --------------------------------------------------
st.subheader("📊 Comparable Sales (Manual Input)")

cols = st.columns(5)
with cols[0]: comp1_price = st.number_input("Comp 1 Price ($)", min_value=0.0, step=500.0)
with cols[1]: comp1_sqft  = st.number_input("Comp 1 Sqft", min_value=0.0, step=10.0)
with cols[2]: comp2_price = st.number_input("Comp 2 Price ($)", min_value=0.0, step=500.0)
with cols[3]: comp2_sqft  = st.number_input("Comp 2 Sqft", min_value=0.0, step=10.0)
with cols[4]: comp3_price = st.number_input("Comp 3 Price ($)", min_value=0.0, step=500.0)

cols2 = st.columns(5)
with cols2[0]: comp3_sqft = st.number_input("Comp 3 Sqft", min_value=0.0, step=10.0)

st.markdown("---")

# --------------------------------------------------
# 🔹 AUTO CALCULATE ARV USING AI (OPTIONAL)
# --------------------------------------------------
if st.button("🤖 Run AI ARV Estimation"):
    ai_prompt = f"""
    Provide ARV estimation based on:
    Subject property:
    - Address: {subject_address}
    - Beds: {subject_beds}
    - Baths: {subject_baths}
    - Sqft: {subject_sqft}
    - Year built: {subject_year}

    Manual comps:
    - Comp1: price={comp1_price}, sqft={comp1_sqft}
    - Comp2: price={comp2_price}, sqft={comp2_sqft}
    - Comp3: price={comp3_price}, sqft={comp3_sqft}

    Return estimated ARV and reasoning.
    """

    response = ASK_AI(ai_prompt)

    st.subheader("🔮 AI ARV Result")
    st.write(response)

st.markdown("---")

# --------------------------------------------------
# END OF FILE
# --------------------------------------------------
