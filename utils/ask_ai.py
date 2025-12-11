import streamlit as st
import json
import openai

# -----------------------------------------------------------
# ASK_AI — Core Engine
# -----------------------------------------------------------
# Sends an address to the AI engine and returns structured JSON:
# - Property details
# - Comparable sales
# - ARV calculation
# - Rehab estimate
# - Neighborhood analysis
# -----------------------------------------------------------

def ASK_AI(address):
    """
    Sends property address to AI and returns structured JSON.
    """

    system_msg = """
    You are a real estate analyst that returns ONLY JSON.
    You must extract real data from:
    - Zillow
    - Redfin
    - Realtor
    - County assessor
    - MLS-style records
    - HomeDisclosure / ATTOM
    - PropStream-like datasets

    Always return JSON with:
    {
      "property": {},
      "comps": [],
      "arv": {},
      "rehab_estimate": {},
      "neighborhood": {}
    }
    """

    user_msg = f"Provide full real estate analysis for this property: {address}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ]
        )
    except Exception as e:
        st.error("OpenAI API error")
        st.error(str(e))
        return None

    raw = response.choices[0].message["content"]

    # Attempt to parse content into JSON
    try:
        data = json.loads(raw)
        return data
    except:
        st.error("AI returned invalid JSON. Showing raw output:")
        st.text(raw)
        return None
