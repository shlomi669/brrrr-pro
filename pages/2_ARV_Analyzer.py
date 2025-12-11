import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Import AI module
from utils.ask_ai import ASK_AI

# Import snapshot storage helpers
from utils.storage import list_snapshots, load_snapshot, load_last_snapshot

# -----------------------------------------------
# PAGE CONFIG
# -----------------------------------------------
st.set_page_config(layout="wide")

st.title("🏡 ARV & Comps Analyzer")
st.caption("Analyze ARV based on sold comparable properties (last 12 months, radius up to 0.7 miles).")

st.markdown("---")

# --------------------------------------------------
# 🔹 LOAD SUBJECT PROPERTY FROM SNAPSHOT
# --------------------------------------------------
st.subheader("📂 Load Subject Property Snapshot")

snapshots = list_snapshots()
selected_snapshot = st.selectbox("📂 Select Snapshot", ["-- Select --"] + snapshots)

# Default values
subject_address = ""
subject_beds = 0.0
subject_baths = 0.0
subject_sqft = 0.0
subject_year = 0

if selected_snapshot != "-- Select --":
    data = load_snapshot(selected_snapshot)

    # Convert data types safely
    subject_address = data.get("address", "")

    # Convert numeric fields (snapshot JSON stores everything as strings)
    try:
        subject_beds = float(data.get("beds", 0))
        subject_baths = float(data.get("baths", 0))
        subject_sqft = float(data.get("sqft", 0))
        subject_year = int(data.get("year_built", 0))
    except:
        st.error("❌ Error converting snapshot numeric values. Please re-save this snapshot.")

    st.success(f"Loaded snapshot: {selected_snapshot}")

else:
    subject_address = ""
    subject_beds = 0.0
    subject_baths = 0.0
    subject_sqft = 0.0
    subject_year = 0

st.markdown("---")

# --------------------------------------------------
# 🔹 SUBJECT PROPERTY FORM
# --------------------------------------------------
st.subheader("🏠 Subject Property Details")

col1, col2 = st.columns(2)

with col1:
    subject_address = st.text_input("Property Address", value=subject_address)

    subject_beds = st.number_input("Beds", value=subject_beds, step=0.5)

    subject_baths = st.number_input("Baths", value=subject_baths, step=0.5)

with col2:
    subject_sqft = st.number_input("Living Area (sqft)", value=subject_sqft, step=10.0)

    subject_year = st.number_input("Year Built", value=subject_year, step=1)

st.markdown("---")

# --------------------------------------------------
# 🔹 MANUAL COMPARABLE SALES INPUT
# --------------------------------------------------
st.subheader("📊 Comparable Sales (Manual Input)")

colA, colB, colC = st.columns(3)

with colA:
    comp1_price = st.number_input("Comp 1 Price ($)", min_value=0.0, step=1000.0)
    comp1_sqft = st.number_input("Comp 1 Sqft", min_value=0.0, step=10.0)

with colB:
    comp2_price = st.number_input("Comp 2 Price ($)", min_value=0.0, step=1000.0)
    comp2_sqft = st.number_input("Comp 2 Sqft", min_value=0.0, step=10.0)

with colC:
    comp3_price = st.number_input("Comp 3 Price ($)", min_value=0.0, step=1000.0)
    comp3_sqft = st.number_input("Comp 3 Sqft", min_value=0.0, step=10.0)

st.markdown("---")

# --------------------------------------------------
# 🔹 AI ARV ESTIMATION
# --------------------------------------------------
if st.button("🤖 Run AI ARV Estimation"):
    st.info("Sending data to AI model...")

    comps = [
        {"price": comp1_price, "sqft": comp1_sqft},
        {"price": comp2_price, "sqft": comp2_sqft},
        {"price": comp3_price, "sqft": comp3_sqft},
    ]

    prompt = {
        "subject": {
            "address": subject_address,
            "beds": subject_beds,
            "baths": subject_baths,
            "sqft": subject_sqft,
            "year": subject_year,
        },
        "comps": comps
    }

    try:
        ai_result = ASK_AI(prompt)
        st.success("AI ARV estimation completed!")
        st.write(ai_result)

    except Exception as e:
        st.error(f"❌ AI request failed: {str(e)}")

