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

# ---------------- CSS - Vintage Mumbai Theme ----------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Poppins:wght@400;500;600&display=swap');

        /* Kraft paper background */
        .stApp, [data-testid="stAppViewContainer"], .main, .block-container {
            background: #b8a088 !important;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E") !important;
            background-blend-mode: multiply !important;
        }

        * {
            font-family: 'Poppins', sans-serif !important;
        }

        .main-title {
            font-family: 'Bebas Neue', sans-serif !important;
            color: #8B0000 !important;
            font-size: 3.5rem !important;
            font-weight: 400 !important;
            text-align: center;
            margin-bottom: 0;
            letter-spacing: 3px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }

        .subtitle {
            color: #3d3d3d !important;
            text-align: center;
            font-size: 1rem !important;
            margin-bottom: 1rem;
            font-weight: 500;
        }

        .line-badge {
            display: inline-block;
            padding: 4px 12px;
            font-size: 0.8rem;
            margin: 0 4px;
            border-radius: 3px;
            font-weight: 600;
            color: #fff !important;
        }
        .western { background: #1a5276 !important; }
        .central { background: #8B0000 !important; }
        .harbour { background: #196f3d !important; }

        /* Buttons - Mumbai taxi yellow */
        .stButton > button {
            background: #d4a017 !important;
            border: none !important;
            color: #1a1a1a !important;
            border-radius: 5px !important;
            padding: 0.5rem 1.2rem;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            background: #8B0000 !important;
            color: #fff !important;
        }

        /* Review cards - like old paper */
        .review-card {
            background: #f5e6d3 !important;
            padding: 14px 16px;
            margin: 10px 0;
            border-left: 4px solid #8B0000;
            border-radius: 0 5px 5px 0;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.15);
        }

        .review-card b {
            color: #2d2d2d !important;
            font-size: 1rem;
            font-weight: 600;
        }

        .review-card small {
            color: #555 !important;
        }

        .section-header {
            color: #8B0000 !important;
            font-family: 'Bebas Neue', sans-serif !important;
            font-size: 1.5rem !important;
            letter-spacing: 2px;
            margin-bottom: 0.5rem;
            border-bottom: 3px solid #8B0000;
            padding-bottom: 5px;
            display: inline-block;
        }

        /* Chat messages */
        .stChatMessage, [data-testid="stChatMessage"] {
            background: #f5e6d3 !important;
            border-radius: 8px !important;
            border: none !important;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.1) !important;
        }

        /* All text */
        p, span, label, div {
            color: #2d2d2d !important;
        }

        h1, h2, h3 {
            color: #8B0000 !important;
        }

        /* Input fields */
        .stChatInput > div, .stChatInput textarea, [data-testid="stChatInput"] > div {
            background: #f5e6d3 !important;
            border: 2px solid #8B0000 !important;
            border-radius: 8px !important;
        }

        input, textarea, select {
            background: #f5e6d3 !important;
            border: 1px solid #a08060 !important;
            color: #2d2d2d !important;
            border-radius: 5px !important;
        }

        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea textarea {
            background: #f5e6d3 !important;
            border: 1px solid #a08060 !important;
            border-radius: 5px !important;
            color: #2d2d2d !important;
        }

        /* Labels */
        .stSelectbox label, .stTextInput label, .stTextArea label, .stSlider label {
            color: #3d3d3d !important;
            font-size: 0.95rem !important;
            font-weight: 500 !important;
        }

        /* Stars - yellow like auto */
        .stars {
            color: #d4a017 !important;
        }

        /* Dividers */
        hr {
            border: none !important;
            border-top: 2px solid #8B0000 !important;
        }

        /* Slider */
        .stSlider > div > div > div {
            background: #8B0000 !important;
        }

        /* Caption */
        .stCaption p {
            color: #666 !important;
        }

        /* Hide streamlit branding */
        #MainMenu, footer {
            visibility: hidden;
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
    st.markdown('<h1 class="main-title">MUMBAI LOCAL</h1>', unsafe_allow_html=True)
    st.markdown('''<p class="subtitle">
        <span class="line-badge western">Western</span>
        <span class="line-badge central">Central</span>
        <span class="line-badge harbour">Harbour</span>
        &nbsp;•&nbsp; 7,500+ trains
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
                    "Welcome to Mumbai Local! 🚃\n\n"
                    "I can help you with train timings, routes & more.\n\n"
                    "**Try asking:**\n"
                    "• Andheri to Churchgate\n"
                    "• AC trains on Western line\n"
                    "• Reviews for Dadar\n"
                    "• Monthly pass price"
                )
            }
        )

    # -------- Chat History --------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # -------- Chat Input --------
    user_input = st.chat_input("Search trains, routes...")

    # -------- Suggested Queries --------
    st.markdown('<p class="section-header">QUICK SEARCH</p>', unsafe_allow_html=True)
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
                        response = f"**{station} Station**\n" + review_summary
                    else:
                        response = f"No reviews for {station} yet. Be the first to write one!"
                    break
            else:
                response = "Which station? Try: *Reviews for Andheri*"
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
    st.markdown('<p class="section-header">WRITE A REVIEW</p>', unsafe_allow_html=True)

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

        review_rating = st.slider("Rating", 1, 5, 4)

        review_comment = st.text_area(
            "Your review",
            placeholder="Share your experience...",
            max_chars=500
        )

        review_name = st.text_input("Name", placeholder="Anonymous")

        submitted = st.form_submit_button("Submit →", use_container_width=True)

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
    st.markdown('<p class="section-header">RECENT REVIEWS</p>', unsafe_allow_html=True)

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
            <small style="color: #636e72;">↑ Be the first to write one</small>
        </div>
        """, unsafe_allow_html=True)

    # Connection status
    st.markdown("---")
    connection = check_sheets_connection()
    if connection['connected']:
        st.caption("⟳ synced")
    else:
        st.caption("◇ local")
