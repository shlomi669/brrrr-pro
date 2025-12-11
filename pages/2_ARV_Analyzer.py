import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Import AI module
from utils.ask_ai import ASK_AI

# Import snapshot storage helpers
from utils.storage import list_snapshots, load_snapshot, load_last_snapshot

st.set_page_config(layout="wide")

st.title("📊 ARV & Comps Analyzer")
st.caption("Analyze ARV based on sold comparable properties (manual input + AI support).")

st.markdown("---")

# --------------------------------------------------
# 🔹 LOAD SUBJECT PROPERTY FROM SNAPSHOT
# --------------------------------------------------
st.subheader("📂 Load Subject Property")

# Load saved snapshots
snapshots = list_snapshots()

selected_snapshot = st.selectbox("📂 Load Property Snapshot", ["-- Select --"] + snapshots)

# Default values
subject_address = ""
subject_beds = 0
subject_baths = 0
subject_sqft = 0
subject_lot = 0
subject_year = 0
subject_price = 0
subject_pps = 0
subject_rtp = 0

if selected_snapshot != "-- Select --":
    data = load_snapshot(selected_snapshot)

    subject_address = data.get("address", "")
    subject_beds = data.get("beds", 0)
    subject_baths = data.get("baths", 0)
    subject_sqft = data.get("sqft", 0)
    subject_lot = data.get("lot_size", 0)
    subject_year = data.get("year_built", 0)
    subject_price = data.get("list_price", 0)
    subject_pps = data.get("price_per_sqft", 0)
    subject_rtp = data.get("rent_to_price", 0)

    st.success(f"Loaded snapshot: {selected_snapshot}")

else:
    st.info("Select a saved property snapshot to load data automatically.")

st.markdown("---")

# --------------------------------------------------
# 🏡 SHOW SUBJECT PROPERTY
# --------------------------------------------------
st.subheader("🏡 Subject Property Details")

col1, col2 = st.columns(2)

with col1:
    st.text_input("Property Address", value=subject_address)
    st.number_input("Beds", value=subject_beds, step=0.5)
    st.number_input("Baths", value=subject_baths, step=0.5)
    st.number_input("List Price ($)", value=subject_price, step=1000.0)

with col2:
    st.number_input("Living Area (sqft)", value=subject_sqft, step=10.0)
    st.number_input("Lot Size (sqft)", value=subject_lot, step=100.0)
    st.number_input("Year Built", value=subject_year, step=1)

# Derived display only
st.markdown("### 🔍 Calculated Metrics")
colA, colB = st.columns(2)
colA.metric("💲 Price per Sqft", f"{subject_pps:,.0f}")
colB.metric("📉 Rent-to-Price %", f"{subject_rtp:.1f}%")

st.markdown("---")

# --------------------------------------------------
# 🔹 COMPARABLE SALES (MANUAL INPUT)
# --------------------------------------------------
st.subheader("📊 Comparable Sales (Manual Input)")

comp_cols = st.columns(6)

comp1_price = comp_cols[0].number_input("Comp 1 Price ($)", min_value=0.0, step=1000.0)
comp1_sqft  = comp_cols[1].number_input("Comp 1 Sqft", min_value=0.0, step=10.0)

comp2_price = comp_cols[2].number_input("Comp 2 Price ($)", min_value=0.0, step=1000.0)
comp2_sqft  = comp_cols[3].number_input("Comp 2 Sqft", min_value=0.0, step=10.0)

comp3_price = comp_cols[4].number_input("Comp 3 Price ($)", min_value=0.0, step=1000.0)
comp3_sqft  = comp_cols[5].number_input("Comp 3 Sqft", min_value=0.0, step=10.0)

# Prepare comps list
comps = []

if comp1_price > 0 and comp1_sqft > 0:
    comps.append({"price": comp1_price, "sqft": comp1_sqft})

if comp2_price > 0 and comp2_sqft > 0:
    comps.append({"price": comp2_price, "sqft": comp2_sqft})

if comp3_price > 0 and comp3_sqft > 0:
    comps.append({"price": comp3_price, "sqft": comp3_sqft})

st.markdown("---")

# --------------------------------------------------
# 🤖 AI ARV ESTIMATION
# --------------------------------------------------
st.subheader("🤖 AI ARV Estimation")

if st.button("🚀 Run AI ARV Estimation"):

    if len(comps) == 0:
        st.error("Please enter at least ONE comparable sale.")
    else:
        with st.spinner("AI analyzing property and comps…"):

            result = ASK_AI.estimate_arv(
                address=subject_address,
                beds=subject_beds,
                baths=subject_baths,
                sqft=subject_sqft,
                year_built=subject_year,
                comps=comps
            )

            st.success("AI ARV estimation completed!")
            st.write(result)

st.markdown("---")

st.info("💡 Tip: Save multiple snapshots in the Lookup page, then select them here to analyze ARV quickly.")
