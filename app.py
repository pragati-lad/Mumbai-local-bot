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
    page_title="Mumbai Local Guru",
    page_icon="🚃",
    layout="wide"
)

# ---------------- CSS - Mumbai Style ----------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        }

        .main-title {
            background: linear-gradient(90deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 0;
        }

        .subtitle {
            color: #a0a0a0;
            text-align: center;
            font-size: 1rem;
            margin-bottom: 1.5rem;
        }

        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            border: none !important;
            color: white !important;
            border-radius: 25px;
            padding: 0.5rem 1.2rem;
            font-size: 0.85rem;
            font-weight: 500;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .review-card {
            background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%);
            padding: 15px;
            border-radius: 15px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }

        .review-card b {
            color: #feca57;
        }

        .review-card small {
            color: #b0b0b0;
        }

        .stat-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        }

        .fun-header {
            color: #48dbfb;
            font-size: 1.3rem;
            font-weight: 600;
        }

        /* Chat styling */
        .stChatMessage {
            background: rgba(255,255,255,0.05) !important;
            border-radius: 15px !important;
        }

        div[data-testid="stMarkdownContainer"] p {
            color: #e0e0e0;
        }

        .stTextInput > div > div > input {
            background: rgba(255,255,255,0.1) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            border-radius: 25px !important;
            color: white !important;
        }

        .stSelectbox > div > div {
            background: rgba(255,255,255,0.1) !important;
            border-radius: 10px !important;
        }

        .stSlider > div > div {
            background: linear-gradient(90deg, #667eea, #764ba2) !important;
        }
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
    st.markdown('<h1 class="main-title">⚡ Mumbai Local Guru</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your ultimate guide to surviving Mumbai locals! ✨</p>', unsafe_allow_html=True)
    st.caption("7,500+ trains ◆ Western • Central • Harbour ◆ AC & Non-AC")

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
                    "Hey! ✦ I'm your **Mumbai Local Guru**!\n\n"
                    "Got **7,500+ trains** data — Western, Central, Harbour — everything!\n\n"
                    "Ask me about:\n"
                    "› **Train times**: *\"Andheri to Churchgate\"*\n"
                    "› **AC Locals**: *\"AC trains on Western line\"*\n"
                    "› **Station gossip**: *\"Reviews for Dadar\"*\n"
                    "› **Info**: *\"Monthly pass price\"*\n\n"
                    "Let's roll! ⚡"
                )
            }
        )

    # -------- Chat History --------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # -------- Chat Input --------
    user_input = st.chat_input("Where do you wanna go? ↗")

    # -------- Suggested Queries --------
    st.markdown('<p class="fun-header">◈ Quick picks for you...</p>', unsafe_allow_html=True)
    cols = st.columns(4)
    for i, s in enumerate(st.session_state.suggestions[:8]):
        if cols[i % 4].button(s, key=f"sugg_{i}"):
            user_input = s

    # -------- Handle Input --------
    if user_input:
        st.session_state.messages.append(
            {"role": "user", "content": user_input}
        )

        with st.chat_message("user"):
            st.markdown(user_input)

        # Check if asking for reviews
        if "review" in user_input.lower() or "kaisa" in user_input.lower():
            for station in STATIONS:
                if station.lower() in user_input.lower():
                    review_summary = get_review_summary(station)
                    if review_summary:
                        response = f"◉ **{station} Station — The Tea**\n" + review_summary
                    else:
                        response = f"No gossip about {station} yet! Be the first to spill! →"
                    break
            else:
                response = "Which station? Try: *\"Reviews for Andheri\"*"
        else:
            response = chatbot_response(user_input)

            for station in STATIONS:
                if station.lower() in user_input.lower():
                    review_summary = get_review_summary(station)
                    if review_summary:
                        response += review_summary
                    break

        with st.chat_message("assistant"):
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
    st.markdown('<p class="fun-header">✦ Spill the Tea!</p>', unsafe_allow_html=True)

    # Review Form
    with st.form("review_form"):
        review_category = st.selectbox(
            "What's this about?",
            ["Station", "Route", "AC Train", "General"]
        )

        if review_category == "Station":
            review_subject = st.selectbox("Pick a station", STATIONS)
        elif review_category == "Route":
            col1, col2 = st.columns(2)
            with col1:
                from_station = st.selectbox("From", STATIONS, key="from")
            with col2:
                to_station = st.selectbox("To", STATIONS, key="to")
            review_subject = f"{from_station} to {to_station}"
        elif review_category == "AC Train":
            review_subject = st.selectbox(
                "Which line?",
                ["AC Western Line", "AC Central Line", "AC Harbour Line"]
            )
        else:
            review_subject = st.text_input("Topic", placeholder="e.g., Peak hour chaos")

        review_rating = st.slider("Your rating", 1, 5, 4, format="%d ⭐")

        review_comment = st.text_area(
            "Your experience",
            placeholder="Tell us about the crowd, cleanliness, timing...",
            max_chars=500
        )

        review_name = st.text_input("Name (optional)", placeholder="Stay anonymous if you want")

        submitted = st.form_submit_button("Drop It! ↗", use_container_width=True)

        if submitted and review_comment:
            add_user_review(
                category=review_category.lower(),
                subject=review_subject,
                rating=review_rating,
                comment=review_comment,
                username=review_name if review_name else "Anonymous"
            )
            st.success("✓ Thanks for the tea! Review added!")
            st.rerun()

    # Recent Reviews - ONLY user submitted reviews
    st.markdown("---")
    st.markdown('<p class="fun-header">◈ Fresh Gossip</p>', unsafe_allow_html=True)

    user_reviews = get_all_reviews_from_sheets()

    if user_reviews:
        sorted_reviews = sorted(user_reviews, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]

        for review in sorted_reviews:
            stars = "★" * review.get("rating", 0) + "☆" * (5 - review.get("rating", 0))
            st.markdown(f"""
            <div class="review-card">
                <b>{review.get('subject', 'Unknown')}</b> <span style="color: #feca57;">{stars}</span><br>
                <small>{review.get('comment', '')[:150]}</small><br>
                <small style="color: #888;">— {review.get('username', 'Anonymous')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="review-card" style="text-align: center;">
            <small>No user reviews yet!</small><br>
            <small style="color: #667eea;">↑ Be the first to drop one ↑</small>
        </div>
        """, unsafe_allow_html=True)

    # Connection status
    st.markdown("---")
    connection = check_sheets_connection()
    if connection['connected']:
        st.caption("⟳ Synced to cloud")
    else:
        st.caption("◈ Local mode")
