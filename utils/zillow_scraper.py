import requests
import json

# -------------------------------------------
# 🔹 Zillow Scraper (Unofficial Free API)
# -------------------------------------------

def get_property_data(zpid: str):
    """
    Fetches basic Zillow property info using an unofficial free endpoint.
    Requires the Zillow property zpid (from the URL).
    """

    url = f"https://zillow.com/graphql/?zpid={zpid}"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

        # Extract important fields (fallback to None if missing)
        price = data.get("price", None)
        sqft = data.get("livingArea", None)
        address = data.get("address", None)

        return {
            "price": price,
            "sqft": sqft,
            "address": address,
        }

    except Exception as e:
        return {"error": str(e)}
