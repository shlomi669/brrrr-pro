import json
import openai

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
        return {"error": str(e)}

    raw = response.choices[0].message["content"]

    # Parse JSON safely
    try:
        return json.loads(raw)
    except:
        return {"error": "Invalid JSON from AI", "raw": raw}
