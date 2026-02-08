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
                linear-gradient(160deg, rgba(15,23,42,0.85) 0%, rgba(30,58,82,0.82) 50%, rgba(15,23,42,0.87) 100%),
                url('data:image/jpeg;base64,{_bg_b64}') !important;
            background-size: cover !important;
            background-position: center !important;
            background-attachment: fixed !important;
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
            font-weight: 600 !important;
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

        .stSlider > div > div > div {{
            background: linear-gradient(90deg, #06b6d4, #22d3ee, #67e8f9) !important;
        }}

        .stCaption, .stCaption p {{
            color: #64748b !important;
            font-size: 0.8rem !important;
        }}

        #MainMenu, footer, header {{ visibility: hidden; height: 0; }}
        .block-container {{ padding-top: 0 !important; }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Layout: Main + Sidebar ----------------
main_col, review_col = st.columns([2, 1])

# ==================================================
# MAIN COLUMN - CHATBOT
# ==================================================
with main_col:
    st.markdown('<h1 class="main-title">Apna Mumbai Local</h1>', unsafe_allow_html=True)
    st.markdown('''<p class="subtitle">
        <span class="line-badge western">Western</span>
        <span class="line-badge central">Central</span>
        <span class="line-badge harbour">Harbour</span>
        <br>Your pocket train guide - 7,500+ trains
    </p>''', unsafe_allow_html=True)

    # ---------------- Session State ----------------
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "suggestions" not in st.session_state:
        st.session_state.suggestions = SUGGESTIONS["default"]

    # ---------------- Initial Bot Message ----------------
    if len(st.session_state.messages) == 0:
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": (
                    "Hey! Welcome to Apna Mumbai Local!\n\n"
                    "Need train timings? Platform info? I got you covered!"
                )
            }
        )

    # -------- Chat History --------
    for msg in st.session_state.messages:
        avatar = "🚃" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    # -------- Chat Input --------
    user_input = st.chat_input("Where to? Try: Dadar to Thane...")

    # -------- Suggested Queries --------
    st.markdown('<p style="color:#64748b !important; font-size:0.75rem !important; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; margin-bottom:6px;">Try These</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, s in enumerate(st.session_state.suggestions[:8]):
        if cols[i % 4].button(s, key=f"sugg_{i}"):
            user_input = s

    # -------- Handle Input --------
    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user", avatar="👤"):
            st.markdown(user_input)

        # Check if asking for reviews
        if "review" in user_input.lower() or "kaisa" in user_input.lower():
            for station in STATIONS:
                if station.lower() in user_input.lower():
                    review_summary = get_review_summary(station)
                    if review_summary:
                        response = f"**{station} Station**\n" + review_summary
                    else:
                        response = f"No reviews for {station} yet. Be the first!"
                    break
            else:
                response = "Which station? Try: *Reviews for Andheri*"
        else:
            response = chatbot_response(user_input)

        with st.chat_message("assistant", avatar="🚃"):
            st.markdown(response)

        st.session_state.messages.append(
            {"role": "assistant", "content": response}
        )

        st.session_state.suggestions = get_related_suggestions(user_input)
        st.rerun()


# ==================================================
# REVIEW COLUMN - SUBMIT & VIEW REVIEWS
# ==================================================
with review_col:
    st.markdown('<p class="section-header">Spill the Tea!</p>', unsafe_allow_html=True)

    # Rating slider OUTSIDE form for live star updates
    review_rating = st.slider("Rate it", 1, 5, 4, key="star_rating")
    st.markdown(f'<p style="text-align:center; font-size:1.8rem; color:#f59e0b; margin-top:-15px; margin-bottom:10px;">{"★" * review_rating}{"☆" * (5 - review_rating)}</p>', unsafe_allow_html=True)

    # Review Form
    with st.form("review_form"):
        review_comment = st.text_area(
            "Your review",
            placeholder="Go ahead and gossip...",
            max_chars=500
        )

        review_name = st.text_input("Name", placeholder="Anonymous")

        submitted = st.form_submit_button("Post It!", use_container_width=True)

        if submitted and review_comment:
            add_user_review(
                category="general",
                subject="General",
                rating=review_rating,
                comment=review_comment,
                username=review_name if review_name else "Anonymous"
            )
            st.success("✓ Review added!")
            st.rerun()

    # Recent Reviews - ONLY user submitted reviews
    st.markdown("---")
    st.markdown('<p class="section-header">Spilled Tea</p>', unsafe_allow_html=True)

    user_reviews = get_all_reviews_from_sheets()

    if user_reviews:
        sorted_reviews = sorted(user_reviews, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]

        for review in sorted_reviews:
            stars = "★" * review.get("rating", 0) + "☆" * (5 - review.get("rating", 0))
            st.markdown(f"""
            <div class="review-card">
                <b>{review.get('subject', 'Unknown')}</b> <span class="stars">{stars}</span><br>
                <small>{review.get('comment', '')[:150]}</small><br>
                <small>— {review.get('username', 'Anonymous')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="review-card" style="text-align: center;">
            No reviews yet!<br>
            <small style="color: #636e72;">common bro drop a comment!</small>
        </div>
        """, unsafe_allow_html=True)

    # Connection status
    st.markdown("---")
    connection = check_sheets_connection()
    if connection['connected']:
        st.caption("⟳ synced")
    else:
        st.caption("◇ local")
