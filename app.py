import streamlit as st
import base64
from train_chatbot_enhanced import chatbot_response
from google_sheets_reviews import (
    add_review_to_sheets as add_user_review,
    get_reviews_for_subject as get_reviews_for,
    get_review_summary_sheets as get_review_summary,
    get_all_reviews_from_sheets,
    check_sheets_connection
)

try:
    from nlp_sentiment import (
        analyze_sentiment, analyze_reviews_batch,
        get_sentiment_summary, format_sentiment_bar
    )
    NLP_SENTIMENT_AVAILABLE = True
except ImportError:
    NLP_SENTIMENT_AVAILABLE = False

# ---------------- Dynamic Suggestions ----------------
SUGGESTIONS = {
    "default": [
        "Andheri to Churchgate",
        "Thane to CSMT",
        "Dadar to Kalyan",
        "Kurla to Panvel",
        "AC trains available?",
        "Monthly pass price",
        "Student concession",
        "Luggage rules",
    ],
    "western": [
        "Bandra to Virar",
        "Borivali to Churchgate",
        "Dadar to Andheri",
        "Churchgate to Borivali",
        "AC on Western line",
        "Reviews for Andheri",
    ],
    "central": [
        "CSMT to Kalyan",
        "Thane to Dadar",
        "Ghatkopar to CSMT",
        "Kurla to Thane",
        "Dadar to Dombivli",
        "Reviews for Thane",
    ],
    "harbour": [
        "CSMT to Panvel",
        "Vashi to CSMT",
        "Kurla to Vashi",
        "Panvel to Kurla",
        "Belapur to CSMT",
        "Reviews for Vashi",
    ],
    "ac": [
        "AC trains Western line",
        "AC trains Central line",
        "AC from Churchgate",
        "AC from Virar",
        "AC local info",
        "AC ticket price",
    ],
    "info": [
        "Monthly pass price",
        "Student concession",
        "Senior citizen discount",
        "Luggage rules",
        "AC trains info",
        "Andheri to Churchgate",
    ],
}

# Station list for reviews
STATIONS = [
    "Churchgate", "Dadar", "Bandra", "Andheri", "Borivali", "Virar",
    "CSMT", "Thane", "Kalyan", "Kurla", "Ghatkopar", "Dombivli",
    "Panvel", "Vashi", "Belapur"
]


def get_related_suggestions(query):
    """Get suggestions related to the user's query."""
    q = query.lower()

    if "ac" in q or "air condition" in q:
        return SUGGESTIONS["ac"]

    if any(word in q for word in ["pass", "concession", "student", "senior", "luggage", "rule"]):
        return SUGGESTIONS["info"]

    western_stations = ["churchgate", "bandra", "andheri", "borivali", "virar", "dadar", "malad", "goregaon"]
    if any(station in q for station in western_stations):
        central_stations = ["csmt", "cst", "thane", "kalyan", "ghatkopar", "dombivli"]
        harbour_stations = ["panvel", "vashi", "belapur"]
        if not any(s in q for s in central_stations + harbour_stations):
            return SUGGESTIONS["western"]

    central_stations = ["csmt", "cst", "thane", "kalyan", "ghatkopar", "kurla", "dombivli", "mulund"]
    if any(station in q for station in central_stations):
        harbour_stations = ["panvel", "vashi", "belapur"]
        if not any(s in q for s in harbour_stations):
            return SUGGESTIONS["central"]

    harbour_stations = ["panvel", "vashi", "belapur", "nerul", "sanpada"]
    if any(station in q for station in harbour_stations):
        return SUGGESTIONS["harbour"]

    return SUGGESTIONS["default"]


# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Mumbai Local",
    page_icon="🚊",
    layout="wide"
)

# ---------------- CSS - Glassmorphism Mumbai Theme ----------------
import pathlib
_bg_path = pathlib.Path(__file__).parent / "bg.jpg"
_bg_b64 = base64.b64encode(_bg_path.read_bytes()).decode()

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

        /* Mumbai doodle background with overlay */
        .stApp, [data-testid="stAppViewContainer"] {{
            background:
                linear-gradient(160deg, rgba(15,23,42,0.88) 0%, rgba(30,58,82,0.85) 50%, rgba(15,23,42,0.88) 100%),
                url('data:image/jpeg;base64,{_bg_b64}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
            background-repeat: repeat !important;
        }}

        .main, .block-container {{
            background: transparent !important;
        }}

        * {{
            font-family: 'Poppins', sans-serif !important;
        }}

        .main-title {{
            background: linear-gradient(135deg, #67e8f9, #22d3ee, #06b6d4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.4rem !important;
            font-weight: 700 !important;
            text-align: center;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }}

        .subtitle {{
            color: rgba(148,163,184,0.9) !important;
            text-align: center;
            font-size: 0.9rem !important;
            margin-bottom: 1.5rem;
            letter-spacing: 0.3px;
        }}

        .line-badge {{
            display: inline-block;
            padding: 6px 14px;
            font-size: 0.7rem;
            margin: 0 4px;
            border-radius: 25px;
            font-weight: 600;
            color: #fff !important;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }}
        .western {{ background: linear-gradient(135deg, #f59e0b, #fbbf24) !important; }}
        .central {{ background: linear-gradient(135deg, #ef4444, #f87171) !important; }}
        .harbour {{ background: linear-gradient(135deg, #06b6d4, #22d3ee) !important; }}

        /* Pill/chip suggestion tags */
        .stButton > button {{
            background: rgba(255,255,255,0.08) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(103,232,249,0.2) !important;
            color: #67e8f9 !important;
            border-radius: 50px !important;
            padding: 0.35rem 1rem !important;
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.15);
            white-space: nowrap;
        }}

        .stButton > button:hover {{
            background: rgba(103,232,249,0.15) !important;
            border-color: #22d3ee !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 18px rgba(34,211,238,0.2);
        }}

        /* Frosted glass cards */
        .review-card {{
            background: rgba(255,255,255,0.07) !important;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            padding: 16px 18px;
            margin: 12px 0;
            border: 1px solid rgba(103,232,249,0.15);
            border-radius: 16px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.2);
        }}

        .review-card b {{
            color: #e2e8f0 !important;
            font-weight: 600;
        }}

        .review-card small {{
            color: #94a3b8 !important;
        }}

        .section-header {{
            color: #22d3ee !important;
            font-size: 1.05rem !important;
            font-weight: 700;
            margin-bottom: 14px;
            letter-spacing: 0.2px;
        }}

        /* Glass chat bubbles */
        .stChatMessage, [data-testid="stChatMessage"] {{
            background: rgba(255,255,255,0.06) !important;
            backdrop-filter: blur(14px);
            -webkit-backdrop-filter: blur(14px);
            border: 1px solid rgba(103,232,249,0.12) !important;
            border-radius: 18px !important;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        }}

        /* Text */
        p, span, div {{
            color: #cbd5e1 !important;
        }}

        label {{
            color: #94a3b8 !important;
            font-size: 0.85rem !important;
            font-weight: 600;
        }}

        strong, b {{
            color: #e2e8f0 !important;
        }}

        /* Glass Inputs */
        .stChatInput > div, [data-testid="stChatInput"] > div {{
            background: rgba(255,255,255,0.08) !important;
            border: 1.5px solid rgba(103,232,249,0.2) !important;
            border-radius: 18px !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
        }}

        input, textarea, select {{
            background: rgba(255,255,255,0.06) !important;
            border: 1.5px solid rgba(103,232,249,0.15) !important;
            color: #e2e8f0 !important;
            border-radius: 12px !important;
        }}

        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea textarea {{
            background: rgba(255,255,255,0.06) !important;
            border: 1.5px solid rgba(103,232,249,0.15) !important;
            border-radius: 12px !important;
            color: #e2e8f0 !important;
        }}

        input::placeholder, textarea::placeholder {{
            color: #64748b !important;
        }}

        .stars {{ color: #fbbf24 !important; }}

        hr {{
            border: none !important;
            border-top: 1px solid rgba(103,232,249,0.1) !important;
            margin: 1.2rem 0 !important;
        }}

        /* Star rating buttons */
        [data-testid="stHorizontalBlock"] button[kind="secondary"][data-testid="stBaseButton-secondary"] {{
            font-size: 1.6rem !important;
        }}

        /* Keep star buttons horizontal on mobile */
        @media (max-width: 640px) {{
            [data-testid="stColumn"] [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(5)) {{
                flex-wrap: nowrap !important;
                gap: 0.25rem !important;
            }}
            [data-testid="stColumn"] [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(5)) > [data-testid="stColumn"] {{
                min-width: 0 !important;
                flex: 1 !important;
                width: auto !important;
            }}
       *

