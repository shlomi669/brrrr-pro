import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("🏡 Property Lookup — Free Data Scraper")
st.caption("Search by Address or MLS — pulls FREE data from Redfin (no API needed)")

# ---------------------------
# Redfin Scraper
# ---------------------------

def scrape_redfin(address):
    try:
        url = f"https://www.redfin.com/stingray/api/gis?location={address}&num_homes=1"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept": "application/json,text/plain,*/*"
        }

        r = requests.get(url, headers=headers, timeout=10)

        if r.status_code != 200:
            return None

        data = r.json()

        if not data.get("homes"):
            return None

        home = data["homes"][0]

        return {
            "price": home.get("price"),
            "beds": home.get("beds"),
            "baths": home.get("baths"),
            "sqft": home.get("sqft"),
            "lot": home.get("lotSize"),
            "year_built": home.get("yearBuilt"),
        }

    except Exception:
        return None

# ---------------------------
# UI — Search Box
# ---------------------------

query = st.text_input("Enter Address or MLS Number")

if st.button("Search Property"):
    if not query:
        st.error("Please enter an address or MLS.")
        st.stop()

    st.info("Searching online data… please wait 2–4 seconds ⏳")

    res = scrape_redfin(query)

    if not res:
        st.error("No data found.")
    else:
        st.success("Data found!")
        st.write("### 📌 Property Info")
        st.write(f"**Price:** ${r

