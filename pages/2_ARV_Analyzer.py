import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(layout="wide")

st.title("📊 ARV & Comps Analyzer")
st.caption("Analyze ARV based on sold comparable properties (last 12 months, radius up to 0.7 miles).")

st.markdown("---")

# -----------------------------
# SUBJECT PROPERTY
# -----------------------------
st.subheader("🏠 Subject Property")

col1, col2 = st.columns(2)
with col1:
    subject_address = st.text_input("Property Address")
    subject_beds = st.number_input("Beds", min_value=0.0, step=0.5)
    subject_baths = st.number_input("Baths", min_value=0.0, step=0.5)
with col2:
    subject_sqft = st.number_input("Living Area (sqft)", min_value=0.0, step=10.0)
    subject_year = st.number_input("Year Built", min_value=1800, max_value=2100, step=1, value=1970)

st.markdown("---")

# -----------------------------
# COMPS TABLE
# -----------------------------
st.subheader("🏘 Comparable Sales (Manual Input)")

st.markdown(
    """
    Enter sold properties that are similar to the subject.  
    **Recommendation:**  
    - Sold within the last 12 months  
    - Within ~0.7 miles  
    - Gather data from: County, MLS, Zillow, Redfin, Realtor, PropStream, BatchLeads, ATTOM, etc.
    """
)

default_data = pd.DataFrame(
    {
        "Address": ["" for _ in range(5)],
        "Sale Date (YYYY-MM-DD)": ["" for _ in range(5)],
        "Sale Price": [0 for _ in range(5)],
        "Beds": [0.0 for _ in range(5)],
        "Baths": [0.0 for _ in range(5)],
        "Sqft": [0.0 for _ in range(5)],
        "Distance (miles)": [0.0 for _ in range(5)],
        "Renovated? (Yes/No)": ["" for _ in range(5)],
    }
)

comps_df = st.data_editor(
    default_data,
    num_rows="dynamic",
    use_container_width=True,
    key="comps_editor",
)

st.markdown("---")

# -----------------------------
# CALCULATE ARV
# -----------------------------
st.subheader("📈 ARV Calculation")

if st.button("Calculate ARV"):
    df = comps_df.copy()

    # Clean & convert
    df["Sale Price"] = pd.to_numeric(df["Sale Price"], errors="coerce")
    df["Sqft"] = pd.to_numeric(df["Sqft"], errors="coerce")
    df["Distance (miles)"] = pd.to_numeric(df["Distance (miles)"], errors="coerce")

    # Parse dates
    df["Sale Date (YYYY-MM-DD)"] = pd.to_datetime(
        df["Sale Date (YYYY-MM-DD)"], errors="coerce"
    )

    # Drop empty rows (no price or no sqft)
    df = df.dropna(subset=["Sale Price", "Sqft"])

    if df.empty:
        st.error("No valid comps entered (need Sale Price & Sqft at minimum).")
    else:
        # Price per sqft
        df["Price per Sqft"] = df["Sale Price"] / df["Sqft"]

        # Filter by last 12 months
        today = datetime.today()
        last_12_months = today - timedelta(days=365)
        df_recent = df[df["Sale Date (YYYY-MM-DD)"] >= last_12_months]

        # Filter by radius <= 0.7 miles
        df_recent_radius = df_recent[df_recent["Distance (miles)"] <= 0.7]

        # If too few comps, relax conditions
        filtered_df = df_recent_radius

        msg = []
        if len(filtered_df) < 3:
            msg.append("Less than 3 comps within 12 months and 0.7 miles.")
            # Try: keep 12 months but ignore radius
            filtered_df = df_recent
        if len(filtered_df) < 3:
            msg.append("Still less than 3 comps – using ALL entered comps as backup.")
            filtered_df = df

        if msg:
            for m in msg:
                st.warning(m)

        # If still empty, nothing to do
        if filtered_df.empty:
            st.error("No comps available after filtering. Please add more data.")
        else:
            # ARV based on price per sqft
            median_ppsqft = filtered_df["Price per Sqft"].median()
            avg_ppsqft = filtered_df["Price per Sqft"].mean()
            min_ppsqft = filtered_df["Price per Sqft"].min()
            max_ppsqft = filtered_df["Price per Sqft"].max()

            if subject_sqft > 0:
                arv_median = median_ppsqft * subject_sqft
                arv_avg = avg_ppsqft * subject_sqft
                arv_low = min_ppsqft * subject_sqft
                arv_high = max_ppsqft * subject_sqft
            else:
                arv_median = arv_avg = arv_low = arv_high = 0

            # Display metrics
            colA, colB, colC, colD = st.columns(4)
            colA.metric("Median $/sqft", f"${median_ppsqft:,.0f}")
            colB.metric("Avg $/sqft", f"${avg_ppsqft:,.0f}")
            colC.metric("Min $/sqft", f"${min_ppsqft:,.0f}")
            colD.metric("Max $/sqft", f"${max_ppsqft:,.0f}")

            st.markdown("---")
            st.subheader("🏁 ARV Estimates (Subject Property)")

            if subject_sqft <= 0:
                st.error("To calculate ARV, please enter Subject Living Area (sqft) above.")
            else:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("ARV (Median $/sqft)", f"${arv_median:,.0f}")
                    st.metric("ARV (Average $/sqft)", f"${arv_avg:,.0f}")
                with col2:
                    st.metric("ARV Low (Min $/sqft)", f"${arv_low:,.0f}")
                    st.metric("ARV High (Max $/sqft)", f"${arv_high:,.0f}")

            st.markdown("---")
            st.subheader("📋 Filtered Comps Used for ARV")

            show_cols = [
                "Address",
                "Sale Date (YYYY-MM-DD)",
                "Sale Price",
                "Beds",
                "Baths",
                "Sqft",
                "Distance (miles)",
                "Renovated? (Yes/No)",
                "Price per Sqft",
            ]

            st.dataframe(
                filtered_df[show_cols].sort_values(
                    by=["Distance (miles)", "Sale Date (YYYY-MM-DD)"],
                    ascending=[True, False],
                ),
                use_container_width=True,
            )
