import streamlit as st
import requests

st.set_page_config(layout="wide")

st.title("🏠 Property Lookup — Free API Data")
st.caption("Pulls FREE property data with no scraping + no blocking")

# -------------------------------------
#  GET PROPERTY DATA FROM API
# -------------------------------------
def get_property_data(address):
    try:
        url = "https://api.openpropertydata.com/v1/address"
        params = {"q": address}

        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        if "property" not in data:
            return None

        p = data["property"]

        return {
            "price": p.get("price", "N/A"),
            "beds": p.get("beds", "N/A"),
            "baths": p.get("baths", "N/A"),
            "sqft": p.get("sqft", "N/A"),
            "year_built": p.get("year_built", "N/A"),
            "zestimate": p.get("zestimate", "N/A"),
            "last_sold_price": p.get("last_sold_price", "N/A"),
            "last_sold_date": p.get("last_sold_date", "N/A"),
            "type": p.get("type", "N/A"),
        }

    except:
        return None


# -------------------------------------
# UI
# -------------------------------------
address = st.text_input("Enter Full Address (USA)", "")

if st.button("Search Property"):
    if not address:
        st.error("Please enter an address.")
    else:
        st.info("Fetching property data… please wait ⏳")

        data = get_property_data(address)

        if not data:
            st.error("No data found for this address.")
        else:
            st.success("Property found! 🎉")

            st.subheader("🏡 Property Details")
            st.write(f"**Price:** {data['price']}")
            st.write(f"**Beds:** {data['beds']}")
            st.write(f"**Baths:** {data['baths']}")
            st.write(f"**Square Feet:** {data['sqft']}")
            st.write(f"**Year Built:** {data['year_built']}")
            st.write(f"**Zestimate:** {data['zestimate']}")
            st.write(f"**Last Sold Price:** {data['last_sold_price']}")
            st.write(f"**Last Sold Date:** {data['last_sold_date']}")
            st.write(f"**Property Type:** {data['type']}")
