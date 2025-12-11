import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import os

# Import AI module
from utils.ask_ai import import ASK_AI

# Import snapshot storage helpers
from utils.storage import list_snapshots, load_snapshot, load_last_snapshot

st.set_page_config(layout="wide")

st.title("🏡 ARV & Comps Analyzer")
st.caption("Analyze ARV based on sold comparable properties (last 12 months, radius up to 0.7 miles).")

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
subject_year = 0

if selected_snapshot != "-- Select --":
    data = load_snapshot(selected_snapshot)
    
    subject_address = data["address"]
    subject_beds = data["beds"]
    subject_baths = data["baths"]
    subject_sqft = data["sqft"]
    subject_year = data["year_built"]

    st.success(f"Loaded snapshot: {selected_snapshot}")

st.markdown("---")

# --------------------------------------------------
# SUBJECT PROPERTY MANUAL EDIT (IF NEEDED)
# --------------------------------------------------
st.subheader("🏠 Subject Property (Edit if needed)")

col1, col2 = st.columns(2)

with col1:
    subject_address = st.text_input("Property Address", value=subject_address)
    subject_beds = st.number_input("Beds", min_value=0.0, step=0.5, value=float(subject_beds))

with col2:
    subject_baths = st.number_input("Baths", min_value=0.0, step=0.5, value=float(subject_baths))
    subject_sqft = st.number_input("Living Area (sqft)", min_value=0.0, step=10.0, value=float(subject_sqft))

subject_year = st.number_input("Year Built", min_value=1800, max_value=2100, step=1, value=int(subject_year))

st.markdown("---")

# --------------------------------------------------
# 🔹 MANUAL COMPARABLES INPUT
# --------------------------------------------------
st.subheader("📊 Comparable Sales (Manual Input)")

st.markdown("Enter up to 6 comparable sold properties:")

default_data = {
    "Address": ["", "", "", "", "", ""],
    "Beds": [0, 0, 0, 0, 0, 0],
    "Baths": [0, 0, 0, 0, 0, 0],
    "Sqft": [0, 0, 0, 0, 0, 0],
    "Year": [0, 0, 0, 0, 0, 0],
    "Sold Price": [0, 0, 0, 0, 0, 0],
    "DOM": [0, 0, 0, 0, 0, 0],
}

df = pd.DataFrame(default_data)

editable_df = st.data_editor(df, use_container_width=True)

st.markdown("---")

# --------------------------------------------------
# 🔹 AI ANALYSIS BUTTON
# --------------------------------------------------
if st.button("🤖 Run AI ARV Analysis"):
    
    # Prepare data for AI
    comps_list = editable_df.to_dict(orient="records")

    ai_prompt = {
        "subject": {
            "address": subject_address,
            "beds": subject_beds,
            "baths": subject_baths,
            "sqft": subject_sqft,
            "year": subject_year,
        },
        "comps": comps_list,
    }

    from utils.ask_ai import ASK_AI
    result = ASK_AI(ai_prompt)

    st.subheader("📈 ARV Analysis Result")
    st.write(result)

st.markdown("---")

# --------------------------------------------------
# END OF FILE
# --------------------------------------------------
