import math
import io
from typing import Dict, Any, Optional

import streamlit as st
import requests
import pandas as pd
from PIL import Image

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="BRRRR PRO - Shlomi",
    page_icon="🏠",
    layout="wide",
)

PRIMARY_COLOR = "#3B82F6"
ACCENT_COLOR = "#F97316"
BG_SOFT = "#F5F7FB"


# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def section_box(title: str, icon: str = "📦"):
    st.markdown(
        f"""
        <div style="
            background-color:{BG_SOFT};
            border-radius:14px;
            padding:14px 18px;
            margin:8px 0;
            border:1px solid #E5E7EB;
        ">
            <div style="font-weight:600;font-size:18px;margin-bottom:4px;">
                {icon} {title}
            </div>
        """,
        unsafe_allow_html=True,
    )


def close_box():
    st.markdown("</div>", unsafe_allow_html=True)


# ----- CALCS -------------------------------------------------------------
def brrrr_core_calc(
    purchase: float,
    rehab: float,
    closing_buy: float,
    arv: float,
    ltv: float,
    rent_monthly: float,
    tax_annual: float,
    insurance_annual: float,
    maintenance_pct: float,
    vacancy_pct: float,
    mgmt_pct: float,
    refi_rate: float,
    refi_years: int,
) -> Dict[str, Any]:
    total_cash_in = purchase + rehab + closing_buy
    loan_amount = arv * (ltv / 100.0)
    cash_left_in = max(total_cash_in - loan_amount, 0)

    annual_rent = rent_monthly * 12
    maintenance = annual_rent * (maintenance_pct / 100.0)
    vacancy = annual_rent * (vacancy_pct / 100.0)
    mgmt = annual_rent * (mgmt_pct / 100.0)

    noi = annual_rent - (tax_annual + insurance_annual + maintenance + vacancy + mgmt)

    # Mortgage payment (אמורטיזציה רגילה)
    r = refi_rate / 100.0 / 12.0
    n = refi_years * 12
    if r > 0:
        monthly_payment = loan_amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
    else:
        monthly_payment = loan_amount / n if n > 0 else 0

    annual_debt_service = monthly_payment * 12
    cashflow_annual = noi - annual_debt_service
    cashflow_monthly = cashflow_annual / 12

    coc = (cashflow_annual / cash_left_in * 100.0) if cash_left_in > 0 else 0
    cap_rate = (noi / purchase * 100.0) if purchase > 0 else 0

    # 70% rule & 1% rule
    seventy_rule_max = arv * 0.7 - rehab
    one_percent_required_rent = purchase * 0.01
    one_percent_ratio = (rent_monthly / purchase * 100.0) if purchase > 0 else 0

    return {
        "total_cash_in": total_cash_in,
        "loan_amount": loan_amount,
        "cash_left_in": cash_left_in,
        "noi": noi,
        "cap_rate": cap_rate,
        "cashflow_annual": cashflow_annual,
        "cashflow_monthly": cashflow_monthly,
        "coc": coc,
        "seventy_rule_max": seventy_rule_max,
        "one_percent_required_rent": one_percent_required_rent,
        "one_percent_ratio": one_percent_ratio,
        "monthly_mortgage": monthly_payment,
        "annual_debt_service": annual_debt_service,
    }


# ----- PLACEHOLDER FETCHERS (להשלמה בשלב הבא) ---------------------------
def fetch_property_from_zillow_or_mls(
    address_or_mls: str,
    zillow_api_key: str = "",
) -> Dict[str, Any]:
    """
    כאן תוסיף בעתיד חיבור אמיתי ל-Zillow / Redfin / MLS.
    כרגע מחזיר ערכים ריקים כדי שהאפליקציה תעבוד.
    """
    return {
        "address": address_or_mls,
        "bedrooms": None,
        "bathrooms": None,
        "year_built": None,
        "lot_size": None,
        "building_sqft": None,
        "zestimate": 0.0,
        "rent_estimate": 0.0,
        "property_tax": 0.0,
        "county_name": "",
        "city": "",
        "state": "",
        "zip": "",
    }


def estimate_rehab_from_image(uploaded_image: Optional[bytes]) -> Dict[str, Any]:
    """
    כאן בעתיד אפשר להשתמש במודלי Vision / שירות חיצוני.
    כרגע: אם יש תמונה – מחזיר הערכת ברירת מחדל.
    """
    if not uploaded_image:
        return {"estimate": 0.0, "notes": "לא הועלתה תמונה – אין הערכה אוטומטית."}

    # placeholder מספר עגול לצורך התחלה
    return {
        "estimate": 25000.0,
        "notes": "הערכת דמו: נא לעדכן ידנית לפי בדיקה מקצועית.",
    }


def fetch_neighborhood_scores_stub() -> Dict[str, Any]:
    """
    כאן ייכנסו בעתיד FBI / Census / וכו'.
    כרגע – ערכים דמיוניים לשם הדגמה בלבד.
    """
    return {
        "crime_score": 6.5,  # 1-10 נמוך טוב, גבוהה רע (להגדרה)
        "socio_econ": 7.2,
        "economic_trend": "Stable",
    }


def fetch_school_scores_stub() -> Dict[str, Any]:
    """
    GreatSchools / Niche / Indiana DOE וכו'.
    כרגע – ערכים דמיוניים.
    """
    return {
        "elem": 8,
        "middle": 7,
        "high": 6,
    }


# -------------------------------------------------
# UI
# -------------------------------------------------
st.markdown(
    f"""
    <div style="
        background:linear-gradient(90deg,{PRIMARY_COLOR},#6366F1);
        padding:18px 24px;
        border-radius:18px;
        color:white;
        margin-bottom:18px;
    ">
        <div style="font-size:24px;font-weight:700;">
            מחשבון BRRRR PRO – אינדיאנפוליס והלאה
        </div>
        <div style="font-size:14px;opacity:0.9;">
            הזן כתובת / מספר MLS, קבל ניתוח עסקה, שכונה, כללים (70% / 1%), ריפיננס ועוד.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ----- SIDEBAR -----------------------------------------------------------
st.sidebar.header("⚙️ הגדרות כלליות")

zillow_key = st.sidebar.text_input("Zillow / RapidAPI Key (אופציונלי)", type="password")
rentometer_key = st.sidebar.text_input("Rentometer API Key (אופציונלי)", type="password")

st.sidebar.markdown("---")
st.sidebar.caption("בהמשך נוסיף עוד מקורות: Redfin, GreatSchools, County APIs וכו'.")

# ----- PROPERTY SEARCH ---------------------------------------------------
section_box("חיפוש נכס – כתובת או MLS#", "🔍")

col_search_1, col_search_2 = st.columns([2, 1])

with col_search_1:
    address_or_mls = st.text_input("הכנס כתובת / MLS#", placeholder="למשל: 4219 Mathews Ave או MLS 22047836")

with col_search_2:
    market = st.text_input("שוק (עיר / מטרו)", value="Indianapolis, IN")

search_clicked = st.button("חפש נכס במקורות אונליין")

property_data: Dict[str, Any] = st.session_state.get("property_data", {})

if search_clicked and address_or_mls.strip():
    property_data = fetch_property_from_zillow_or_mls(address_or_mls, zillow_key)
    st.session_state["property_data"] = property_data
    st.success("בוצע חיפוש דמו (ניתן להרחיב ל-API אמיתי).")

if property_data:
    st.markdown(
        f"**נכס:** {property_data.get('address','')}  |  "
        f"{property_data.get('city','')} {property_data.get('state','')} {property_data.get('zip','')}"
    )

close_box()

# ----- IMAGE UPLOAD & REHAB ---------------------------------------------
section_box("העלאת תמונת נכס – הערכת שיפוץ", "🛠️")

col_img_1, col_img_2 = st.columns([1, 2])

with col_img_1:
    uploaded_file = st.file_uploader("בחר תמונה (חזית / פנים הנכס)", type=["jpg", "jpeg", "png"])
    rehab_auto_est = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="תצוגת תמונת הנכס", use_column_width=True)
        rehab_auto = estimate_rehab_from_image(uploaded_file.getvalue())
        rehab_auto_est = rehab_auto["estimate"]
        st.info(rehab_auto["notes"])

with col_img_2:
    default_rehab = rehab_auto_est if rehab_auto_est is not None else 30000.0
    rehab_cost = st.number_input("עלות שיפוץ משוערת ($)", value=float(default_rehab), step=500.0)

    show_breakdown = st.checkbox("הצג/הכנס פירוט הוצאות שיפוץ", value=False)
    if show_breakdown:
        st.markdown("**פירוט (דמו – ניתן להתאים):**")
        c1, c2, c3 = st.columns(3)
        with c1:
            rehab_paint = st.number_input("צביעה", value=3000.0, step=500.0)
            rehab_floor = st.number_input("ריצוף", value=5000.0, step=500.0)
        with c2:
            rehab_kitchen = st.number_input("מטבח", value=8000.0, step=500.0)
            rehab_bath = st.number_input("אמבטיות", value=6000.0, step=500.0)
        with c3:
            rehab_roof = st.number_input("גג/חוץ", value=4000.0, step=500.0)
            rehab_other = st.number_input("אחר", value=3000.0, step=500.0)

        sum_detail = rehab_paint + rehab_floor + rehab_kitchen + rehab_bath + rehab_roof + rehab_other
        st.markdown(f"**סה\"כ פירוט:** ${sum_detail:,.0f}")
        if abs(sum_detail - rehab_cost) > 1:
            st.warning("שווה לעדכן את 'עלות שיפוץ משוערת' שתשקף את סה\"כ הפירוט.")

close_box()

# ----- FIXED EXPENSES & RENTS -------------------------------------------
section_box("פרטי נכס, שכירות והוצאות קבועות", "📄")

col_a, col_b, col_c = st.columns(3)

with col_a:
    purchase_price = st.number_input("מחיר רכישה ($)", value=85000.0, step=1000.0)
    arv = st.number_input(
        "שווי לאחר שיפוץ – ARV ($)",
        value=float(property_data.get("zestimate", 120000.0) or 120000.0),
        step=1000.0,
    )
    year_built = st.number_input(
        "שנת בנייה",
        value=float(property_data.get("year_built", 1960) or 1960),
        step=1.0,
    )

with col_b:
    rent_zillow = float(property_data.get("rent_estimate", 0.0) or 0.0)
    rent_input_default = rent_zillow if rent_zillow > 0 else 1200.0
    rent_monthly = st.number_input("שכירות חודשית משוערת ($)", value=rent_input_default, step=50.0)
    tax_annual = st.number_input(
        "מיסי נכס שנתיים ($)",
        value=float(property_data.get("property_tax", 2000.0) or 2000.0),
        step=100.0,
    )
    insurance_annual = st.number_input("ביטוח שנתי ($)", value=1200.0, step=100.0)

with col_c:
    maintenance_pct = st.slider("אחוז תחזוקה מהשכירות", 5, 20, 8)
    vacancy_pct = st.slider("אחוז חוסר תפוסה", 3, 20, 5)
    mgmt_pct = st.slider("אחוז ניהול נכס", 8, 15, 10)

close_box()

# ----- REFINANCE SETTINGS & RULES ---------------------------------------
section_box("ריפיננס וכללי 70% / 1%", "🏦")

col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    ltv = st.slider("LTV בריפיננס (%)", 60, 80, 75)
    refi_rate = st.number_input("ריבית ריפיננס שנתית (%)", value=8.0, step=0.25)
    refi_years = st.number_input("משך הלוואה (שנים)", value=30, step=1)

with col_r2:
    seventy_rule_base = st.slider("אחוז כלל 70 (ניתן לשינוי)", 60, 80, 70)
    seventy_max_offer = arv * (seventy_rule_base / 100.0) - rehab_cost
    st.markdown(f"**מקסימום הצעה לפי כלל {seventy_rule_base}%:** ${seventy_max_offer:,.0f}")

with col_r3:
    one_percent_required = purchase_price * 0.01
    st.markdown(f"**שכירות נדרשת לפי כלל 1%:** ${one_percent_required:,.0f}")
    if rent_monthly >= one_percent_required:
        st.success("השכירות עומדת בכלל 1% (או יותר).")
    else:
        st.warning("השכירות נמוכה מכלל 1% – בדוק שוב את העסקה / המחיר.")

close_box()

# ----- NEIGHBORHOOD & SCHOOLS (STUB) ------------------------------------
cols_top = st.columns(2)

with cols_top[0]:
    section_box("דירוג שכונה (דמו – להמשך פיתוח)", "🏙️")
    neigh = fetch_neighborhood_scores_stub()
    st.markdown(
        f"""
        • **דירוג פשיעה (1-10, נמוך טוב):** {neigh['crime_score']:.1f}  
        • **ציון סוציו-אקונומי (1-10):** {neigh['socio_econ']:.1f}  
        • **מגמה כלכלית:** {neigh['economic_trend']}
        """
    )
    close_box()

with cols_top[1]:
    section_box("בתי ספר באזור (דמו)", "🏫")
    schools = fetch_school_scores_stub()
    st.markdown(
        f"""
        • **יסודי:** {schools['elem']}/10  
        • **חטיבה:** {schools['middle']}/10  
        • **תיכון:** {schools['high']}/10  
        """
    )
    close_box()

# ----- MAIN CALC --------------------------------------------------------
calc_clicked = st.button("🔮 חשב ניתוח BRRRR מלא")

if calc_clicked:
    results = brrrr_core_calc(
        purchase=purchase_price,
        rehab=rehab_cost,
        closing_buy=0.0,  # אפשר להוסיף שדה בהמשך
        arv=arv,
        ltv=ltv,
        rent_monthly=rent_monthly,
        tax_annual=tax_annual,
        insurance_annual=insurance_annual,
        maintenance_pct=maintenance_pct,
        vacancy_pct=vacancy_pct,
        mgmt_pct=mgmt_pct,
        refi_rate=refi_rate,
        refi_years=int(refi_years),
    )

    st.markdown("---")
    st.subheader("📊 תוצאות עיקריות")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Cash Left In Deal", f"${results['cash_left_in']:,.0f}")
    m2.metric("Monthly Cashflow", f"${results['cashflow_monthly']:,.0f}")
    m3.metric("CoC Return", f"{results['coc']:.1f}%")
    m4.metric("Cap Rate", f"{results['cap_rate']:.1f}%")

    st.markdown("### טבלת נתונים מלאה")
    df = pd.DataFrame(
        {
            "מדד": [
                "Total Cash In",
                "Loan Amount",
                "Cash Left In Deal",
                "NOI (שנתי)",
                "Cap Rate %",
                "Monthly Cashflow",
                "Annual Cashflow",
                "CoC Return %",
                "70% Rule Max Offer",
                "1% Rule Required Rent",
                "1% Rule Ratio %",
                "Monthly Mortgage Payment",
                "Annual Debt Service",
            ],
            "ערך": [
                results["total_cash_in"],
                results["loan_amount"],
                results["cash_left_in"],
                results["noi"],
                results["cap_rate"],
                results["cashflow_monthly"],
                results["cashflow_annual"],
                results["coc"],
                results["seventy_rule_max"],
                results["one_percent_required_rent"],
                results["one_percent_ratio"],
                results["monthly_mortgage"],
                results["annual_debt_service"],
            ],
        }
    )
    st.dataframe(df, use_container_width=True)

st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#9CA3AF;font-size:12px;margin-top:16px;'>"
    "BRRRR PRO • Built for Shlomi • גרסת דמו ראשונה – נוכל לשפר אחרי שנראה איך זה מרגיש."
    "</div>",
    unsafe_allow_html=True,
)

