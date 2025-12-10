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

        if not data["homes"]:
            return None

        home = data["homes"][0]

        return {
            "price": home.get("price"),
            "beds": home.get("beds"),
            "baths": home.get("baths"),
            "sqft": home.get("sqFt"),
            "lot": home.get("lotSize"),
            "year": home.get("yearBuilt"),
            "url": f"https://www.redfin.com{home.get('url')}"
        }

    except Exception as e:
        return None
