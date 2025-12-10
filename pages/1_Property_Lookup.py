import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(layout="wide")

st.title("🏠 Property Lookup — Free Data Scraper")
st.caption("Search by Address or MLS — pulls FREE data from Zillow, Redfin & Realtor (no API needed)")

# ---------------------------------
# Search Input
# ---------------------------------
query = st.text_input("Enter Address or MLS Number")

if st.button("Search Property"):
    if not query:
        st.error("Please enter an address or MLS.")
        st.stop()

    st.info("Searching online data… please wait 2–4 seconds ⏳")

    # -----------------------------
    # SCRAPER FUNCTIONS
    # -----------------------------
    def fetch_html(url):
        """Fetch raw HTML safely."""
        try:
            r = requests.get(url, headers={
                "User-Agent": "Mozilla/5.0"
            }, timeout=8)
            if r.status_code == 200:
                return r.text
            return None
        except:
            return None

    # Zillow URL Builder
    zillow_url = f"https://www.zillow.com/homes/{query.replace(' ', '-')}_rb/"
    redfin_url = f"https://www.redfin.com/stingray/do/location-autocomplete?location={query.replace(' ', '%20')}"
    realtor_url = f"https://www.realtor.com/realestateandhomes-search/{query.replace(' ', '-')}"
    
    # -----------------------------
    # Zillow Scrape
    # -----------------------------
    zillow_html = fetch_html(zillow_url)
    zillow_data = {}

    if zillow_html:
        soup = BeautifulSoup(zillow_html, "html.parser")

        try:
            price = soup.find("span", {"data-testid": "price"}).text
        except:
            price = "N/A"

        try:
            beds = soup.find("span", {"data-testid": "bed-bath-beyond-beds"}).text
        except:
            beds = "N/A"

        try:
            baths = soup.find("span", {"data-testid": "bed-bath-beyond-baths"}).text
        except:
            baths = "N/A"

        try:
            sqft = soup.find("span", {"data-testid": "bed-bath-beyond-sqft"}).text
        except:
            sqft = "N/A"

        try:
            year = soup.find(string="Year built").find_next().text
        except:
            year = "N/A"

        zillow_data = {
            "Price": price,
            "Beds": beds,
            "Baths": baths,
            "SqFt": sqft,
            "Year Built": year,
            "Link": zillow_url
        }

    # -----------------------------
    # Redfin Basic Scrape
    # -----------------------------
    redfin_html = fetch_html(redfin_url)
    redfin_data = {}

    try:
        if redfin_html:
            redfin_json = redfin_html
            redfin_data = {"Found": True, "Link": redfin_url}
    except:
        redfin_data = {"Found": False}

    # -----------------------------
    # Realtor Scrape
    # -----------------------------
    realtor_html = fetch_html(realtor_url)
    realtor_data = {}

    if realtor_html:
        realtor_data = {"Found": True, "Link": realtor_url}
    else:
        realtor_data = {"Found": False}

    # ---------------------------------
    # Display Results
    # ---------------------------------
    st.success("Property data loaded!")

    st.subheader("📌 Basic Property Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write("### Zillow")
        st.json(zillow_data)

    with col2:
        st.write("### Redfin")
        st.json(redfin_data)

        st.write("### Realtor")
        st.json(realtor_data)

    st.markdown("---")
    st.write("🌐 *All scraping uses public web data, free, no API required.*")
