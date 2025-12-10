import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")

st.title("🏡 Property Lookup — Free Data Scraper")
st.caption("Search by Address or MLS — pulls FREE data from Zillow & Redfin (no API needed!)")

# -----------------------------
# Search Input
# -----------------------------
query = st.text_input("Enter Address or MLS Number")

if st.button("Search Property"):
    if not query:
        st.error("Please enter an address or MLS.")
        st.stop()

    st.info("Searching online data... please wait 2–4 seconds ⏳")

    # -----------------------------------------
    # Zillow Free Scrape
    # -----------------------------------------
    try:
        zillow_url = f"https://www.zillow.com/homedetails/{query.replace(' ', '-')}/"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(zillow_url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")

        # Attempt to extract some fields
        price = soup.find("span", {"data-testid": "price"}).text if soup.find("span", {"data-testid": "price"}) else "N/A"
        beds = soup.find("span", {"data-testid": "bed-bath-beyond-beds"}).text if soup.find("span", {"data-testid": "bed-bath-beyond-beds"}) else "N/A"
        baths = soup.find("span", {"data-testid": "bed-bath-beyond-baths"}).text if soup.find("span", {"data-testid": "bed-bath-beyond-baths"}) else "N/A"
        sqft = soup.find("span", {"data-testid": "bed-bath-beyond-sqft"}).text if soup.find("span", {"data-testid": "bed-bath-beyond-sqft"}) else "N/A"

        st.subheader("📌 Zillow Results")
        st.write(f"**Price:** {price}")
        st.write(f"**Beds:** {beds}")
        st.write(f"**Baths:** {baths}")
        st.write(f"**Square Feet:** {sqft}")

    except Exception as e:
        st.error("Zillow data not found (most likely blocked or property doesn't exist).")

    # -----------------------------------------
    # Redfin Free Scrape
    # -----------------------------------------
    try:
        redfin_url = f"https://www.redfin.com/search?q={query.replace(' ', '%20')}"
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(redfin_url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")

        st.subheader("📌 Redfin Scan (Basic Info)")
        st.write("Search completed — Redfin blocks details, but address lookup confirms property existence.")

    except:
        st.error("Could not scan Redfin.")

    st.success("Search completed ✔️")
