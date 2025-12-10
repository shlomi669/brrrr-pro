import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")

st.title("🏠 Property Lookup — Free Data Scraper")
st.caption("Pulls FREE property data from Realtor.com (No API Needed)")

# --------------------------------------
# Function: Realtor Scraper
# --------------------------------------
def scrape_realtor(address):
    try:
        # Convert address into URL-friendly format
        query = address.replace(" ", "-").replace(",", "")
        url = f"https://www.realtor.com/realestateandhomes-search/{query}"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Accept-Language": "en-US,en;q=0.9",
        }

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract price
        price_tag = soup.select_one("[data-testid='price']")
        price = price_tag.text.strip() if price_tag else "N/A"

        # Extract beds
        beds_tag = soup.select_one("[data-testid='beds']")
        beds = beds_tag.text.strip() if beds_tag else "N/A"

        # Extract baths
        baths_tag = soup.select_one("[data-testid='baths']")
        baths = baths_tag.text.strip() if baths_tag else "N/A"

        # Extract square feet
        sqft_tag = soup.select_one("[data-testid='sqft']")
        sqft = sqft_tag.text.strip() if sqft_tag else "N/A"

        # Extract year built
        year_built = "N/A"
        details = soup.find_all("li")
        for d in details:
            if "Built" in d.text:
                year_built = d.text.replace("Built", "").strip()
                break

        return {
            "price": price,
            "beds": beds,
            "baths": baths,
            "sqft": sqft,
            "year_built": year_built,
        }

    except Exception:
        return None


# --------------------------------------
# UI
# --------------------------------------
address = st.text_input("Enter Full Address")

if st.button("Search Property"):
    if not address:
        st.error("Please enter an address.")
    else:
        st.info("Searching Realtor.com… please wait 2–4 seconds ⏳")

        data = scrape_realtor(address)

        if not data:
            st.error("No data found. Try a different address.")
        else:
            st.success("Property Found!")

            st.subheader("🏡 Property Details")
            st.write(f"**Price:** {data['price']}")
            st.write(f"**Beds:** {data['beds']}")
            st.write(f"**Baths:** {data['baths']}")
            st.write(f"**Square Feet:** {data['sqft']}")
            st.write(f"**Year Built:** {data['year_built']}")
