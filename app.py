import streamlit as st
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

# ---------------- CSS - Aesthetic Summer Theme ----------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

        /* Soft aesthetic gradient */
        .stApp, [data-testid="stAppViewContainer"] {
            background: linear-gradient(160deg, #fdf4ff 0%, #fce7f3 20%, #fff1f2 40%, #fef3c7 60%, #ecfeff 80%, #f0fdf4 100%) !important;
        }

        .main, .block-container {
            background: transparent !important;
        }

        * {
            font-family: 'Quicksand', sans-serif !important;
        }

        .main-title {
            background: linear-gradient(135deg, #f472b6, #c084fc, #60a5fa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.4rem !important;
            font-weight: 700 !important;
            text-align: center;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }

        .subtitle {
            color: #9ca3af !important;
            text-align: center;
            font-size: 0.9rem !important;
            margin-bottom: 1.5rem;
            letter-spacing: 0.3px;
        }

        .line-badge {
            display: inline-block;
            padding: 6px 14px;
            font-size: 0.7rem;
            margin: 0 4px;
            border-radius: 25px;
            font-weight: 600;
            color: #fff !important;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .western { background: linear-gradient(135deg, #fb923c, #fdba74) !important; }
        .central { background: linear-gradient(135deg, #f472b6, #f9a8d4) !important; }
        .harbour { background: linear-gradient(135deg, #38bdf8, #7dd3fc) !important; }

        /* Pill/chip suggestion tags */
        .stButton > button {
            background: rgba(255,255,255,0.7) !important;
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(244, 114, 182, 0.25) !important;
            color: #be185d !important;
            border-radius: 50px !important;
            padding: 0.35rem 1rem !important;
            font-size: 0.78rem !important;
            font-weight: 600 !important;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(244, 114, 182, 0.1);
            white-space: nowrap;
        }

        .stButton > button:hover {
            background: linear-gradient(135deg, #fce7f3, #fdf4ff) !important;
            border-color: #f472b6 !important;
            transform: translateY(-1px);
            box-shadow: 0 4px 14px rgba(244, 114, 182, 0.2);
        }

        /* Frosted glass cards */
        .review-card {
            background: rgba(255,255,255,0.75) !important;
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            padding: 16px 18px;
            margin: 12px 0;
            border: 1px solid rgba(244, 114, 182, 0.2);
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.04);
        }

        .review-card b {
            color: #374151 !important;
            font-weight: 600;
        }

        .review-card small {
            color: #9ca3af !important;
        }

        .section-header {
            color: #db2777 !important;
            font-size: 1.05rem !important;
            font-weight: 700;
            margin-bottom: 14px;
            letter-spacing: 0.2px;
        }

        /* Aesthetic chat bubbles */
        .stChatMessage, [data-testid="stChatMessage"] {
            background: rgba(255,255,255,0.7) !important;
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(244, 114, 182, 0.15) !important;
            border-radius: 18px !important;
            box-shadow: 0 4px 16px rgba(0,0,0,0.03);
        }

        /* Text */
        p, span, div {
            color: #4b5563 !important;
        }

        label {
            color: #9ca3af !important;
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }

        strong, b {
            color: #374151 !important;
        }

        /* Aesthetic Inputs */
        .stChatInput > div, [data-testid="stChatInput"] > div {
            background: rgba(255,255,255,0.85) !important;
            border: 1.5px solid rgba(244, 114, 182, 0.25) !important;
            border-radius: 18px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        }

        input, textarea, select {
            background: rgba(255,255,255,0.95) !important;
            border: 1.5px solid rgba(244, 114, 182, 0.2) !important;
            color: #374151 !important;
            border-radius: 12px !important;
        }

        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea textarea {
            background: rgba(255,255,255,0.95) !important;
            border: 1.5px solid rgba(244, 114, 182, 0.2) !important;
            border-radius: 12px !important;
            color: #374151 !important;
        }

        input::placeholder, textarea::placeholder {
            color: #d1d5db !important;
        }

        .stars { color: #f472b6 !important; }

        hr {
            border: none !important;
            border-top: 1px solid rgba(244, 114, 182, 0.15) !important;
            margin: 1.2rem 0 !important;
        }

        .stSlider > div > div > div {
            background: linear-gradient(90deg, #f472b6, #c084fc, #60a5fa) !important;
        }

        .stCaption, .stCaption p {
            color: #d1d5db !important;
            font-size: 0.8rem !important;
        }

        #MainMenu, footer, header { visibility: hidden; height: 0; }
        .block-container { padding-top: 0 !important; }
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
    st.markdown('<p style="color:#d1d5db !important; font-size:0.75rem !important; font-weight:600; letter-spacing:0.5px; text-transform:uppercase; margin-bottom:6px;">Try These</p>', unsafe_allow_html=True)
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
        review_category = st.selectbox(
            "Category",
            ["Station", "Route", "AC Train", "General"]
        )

        if review_category == "Station":
            review_subject = st.selectbox("Station", STATIONS)
        elif review_category == "Route":
            col1, col2 = st.columns(2)
            with col1:
                from_station = st.selectbox("From", STATIONS, key="from")
            with col2:
                to_station = st.selectbox("To", STATIONS, key="to")
            review_subject = f"{from_station} to {to_station}"
        elif review_category == "AC Train":
            review_subject = st.selectbox(
                "Line",
                ["AC Western Line", "AC Central Line", "AC Harbour Line"]
            )
        else:
            review_subject = st.text_input("Topic", placeholder="e.g., Peak hour experience")

        review_comment = st.text_area(
            "Your review",
            placeholder="Go ahead and gossip...",
            max_chars=500
        )

        review_name = st.text_input("Name", placeholder="Anonymous")

        submitted = st.form_submit_button("Post It!", use_container_width=True)

        if submitted and review_comment:
            add_user_review(
                category=review_category.lower(),
                subject=review_subject,
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
            <small style="color: #636e72;">Be the first to drop one</small>
        </div>
        """, unsafe_allow_html=True)

    # Connection status
    st.markdown("---")
    connection = check_sheets_connection()
    if connection['connected']:
        st.caption("⟳ synced")
    else:
        st.caption("◇ local")
