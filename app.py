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

# ---------------- CSS - Vintage Indian Matchbox Theme ----------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Abril+Fatface&family=Work+Sans:wght@400;500;600;700&display=swap');

        /* Cream paper background */
        .stApp, [data-testid="stAppViewContainer"] {
            background: #f4efe4 !important;
        }

        .main, .block-container {
            background: transparent !important;
        }

        * {
            font-family: 'Work Sans', sans-serif !important;
        }

        .main-title {
            font-family: 'Abril Fatface', serif !important;
            color: #c41e3a !important;
            font-size: 2.8rem !important;
            font-weight: 400 !important;
            text-align: center;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 2px;
        }

        .subtitle {
            color: #5a4a3a !important;
            text-align: center;
            font-size: 0.95rem !important;
            margin-bottom: 1rem;
            font-weight: 500;
        }

        /* Train line badges - matchbox style */
        .line-badge {
            display: inline-block;
            padding: 5px 12px;
            font-size: 0.8rem;
            margin: 0 4px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            border: 2px solid;
        }
        .western {
            background: #1a4b8c !important;
            color: #f4efe4 !important;
            border-color: #0f2d54 !important;
        }
        .central {
            background: #c41e3a !important;
            color: #f4efe4 !important;
            border-color: #8b1528 !important;
        }
        .harbour {
            background: #2d5a27 !important;
            color: #f4efe4 !important;
            border-color: #1a3517 !important;
        }

        /* Buttons - vintage matchbox style */
        .stButton > button {
            background: #d4a017 !important;
            border: 2px solid #8b6914 !important;
            color: #1a1a1a !important;
            border-radius: 0 !important;
            padding: 0.5rem 1.2rem;
            font-size: 0.85rem !important;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            background: #c41e3a !important;
            border-color: #8b1528 !important;
            color: #f4efe4 !important;
        }

        /* Cards - vintage label style */
        .review-card {
            background: #fff9e6 !important;
            padding: 14px 16px;
            margin: 10px 0;
            border: 3px solid #c41e3a;
            box-shadow: 4px 4px 0px #5a4a3a;
        }

        .review-card b {
            color: #c41e3a !important;
            font-size: 1rem;
            font-weight: 700;
        }

        .review-card small {
            color: #5a4a3a !important;
        }

        .section-header {
            font-family: 'Abril Fatface', serif !important;
            color: #c41e3a !important;
            font-size: 1.3rem !important;
            font-weight: 400;
            margin-bottom: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            border-bottom: 3px solid #d4a017;
            padding-bottom: 5px;
            display: inline-block;
        }

        /* Chat messages */
        .stChatMessage, [data-testid="stChatMessage"] {
            background: #fff9e6 !important;
            border: 2px solid #5a4a3a !important;
            border-radius: 0 !important;
        }

        /* Text colors */
        p, span, div {
            color: #3a3a3a !important;
        }

        label {
            color: #5a4a3a !important;
            font-size: 0.9rem !important;
            font-weight: 600 !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        strong, b {
            color: #c41e3a !important;
        }

        /* Input fields */
        .stChatInput > div, [data-testid="stChatInput"] > div {
            background: #fff9e6 !important;
            border: 2px solid #5a4a3a !important;
            border-radius: 0 !important;
        }

        .stChatInput input, .stChatInput textarea {
            color: #3a3a3a !important;
        }

        input, textarea, select {
            background: #fff9e6 !important;
            border: 2px solid #5a4a3a !important;
            color: #3a3a3a !important;
            border-radius: 0 !important;
        }

        input::placeholder, textarea::placeholder {
            color: #8a7a6a !important;
        }

        .stTextInput > div > div > input,
        .stSelectbox > div > div,
        .stTextArea textarea {
            background: #fff9e6 !important;
            border: 2px solid #5a4a3a !important;
            border-radius: 0 !important;
            color: #3a3a3a !important;
        }

        /* Stars - golden yellow */
        .stars {
            color: #d4a017 !important;
        }

        /* Dividers */
        hr {
            border: none !important;
            border-top: 3px solid #c41e3a !important;
            margin: 1rem 0 !important;
        }

        /* Slider */
        .stSlider > div > div > div {
            background: #c41e3a !important;
        }

        /* Form */
        .stForm {
            background: transparent !important;
        }

        /* Caption */
        .stCaption, .stCaption p {
            color: #8a7a6a !important;
            font-size: 0.8rem !important;
        }

        /* Success message */
        .stSuccess {
            background: #2d5a27 !important;
            color: #f4efe4 !important;
            border-radius: 0 !important;
        }

        /* Hide streamlit branding */
        #MainMenu, footer, header {
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
    st.markdown('<h1 class="main-title">Mumbai Local</h1>', unsafe_allow_html=True)
    st.markdown('''<p class="subtitle">
        <span class="line-badge western">Western</span>
        <span class="line-badge central">Central</span>
        <span class="line-badge harbour">Harbour</span>
        <br><span style="font-size: 0.85rem;">7,500+ Real Train Schedules</span>
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
    st.markdown('<p class="section-header">Quick Search</p>', unsafe_allow_html=True)
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
    st.markdown('<p class="section-header">Write a Review</p>', unsafe_allow_html=True)

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
    st.markdown('<p class="section-header">Recent Reviews</p>', unsafe_allow_html=True)

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
