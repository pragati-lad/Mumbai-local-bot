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

# ---------------- CSS - Notebook Doodle Theme ----------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Patrick+Hand&display=swap');

        .stApp {
            background-color: #f8f6f1;
            background-image:
                linear-gradient(#e8e6e1 1px, transparent 1px),
                linear-gradient(90deg, #e8e6e1 1px, transparent 1px),
                linear-gradient(90deg, #c94c4c 2px, transparent 2px);
            background-size: 18px 18px, 18px 18px, 100% 100%;
            background-position: 0 0, 0 0, 60px 0;
            font-family: 'Patrick Hand', cursive;
        }

        .main-title {
            font-family: 'Patrick Hand', cursive;
            color: #2d2d2d;
            font-size: 2.6rem;
            font-weight: 400;
            text-align: center;
            margin-bottom: 5px;
        }

        .subtitle {
            font-family: 'Patrick Hand', cursive;
            color: #555;
            text-align: center;
            font-size: 1.2rem;
            margin-bottom: 1rem;
        }

        .line-badge {
            display: inline-block;
            padding: 3px 10px;
            font-size: 0.85rem;
            margin: 0 3px;
            font-family: 'Patrick Hand', cursive;
            border: 2px solid #2d2d2d;
            border-radius: 3px;
            background: transparent;
            color: #2d2d2d;
        }

        .stButton > button {
            background: transparent !important;
            border: 2px solid #2d2d2d !important;
            color: #2d2d2d !important;
            border-radius: 5px;
            padding: 0.4rem 1rem;
            font-size: 0.9rem;
            font-family: 'Patrick Hand', cursive !important;
            transition: all 0.2s ease;
        }

        .stButton > button:hover {
            background: #2d2d2d !important;
            color: #f8f6f1 !important;
        }

        .review-card {
            background: #fff;
            padding: 12px 14px;
            margin: 8px 0;
            border: 2px solid #2d2d2d;
            border-radius: 3px;
        }

        .review-card b {
            color: #2d2d2d;
            font-family: 'Patrick Hand', cursive;
            font-size: 1.1rem;
        }

        .review-card small {
            color: #666;
        }

        .section-header {
            font-family: 'Patrick Hand', cursive;
            color: #2d2d2d;
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
            border-bottom: 2px solid #2d2d2d;
            padding-bottom: 4px;
            display: inline-block;
        }

        /* Chat styling */
        .stChatMessage {
            background: #fff !important;
            border: 2px solid #2d2d2d !important;
            border-radius: 3px !important;
        }

        div[data-testid="stMarkdownContainer"] p {
            color: #2d2d2d !important;
            font-family: 'Patrick Hand', cursive !important;
        }

        div[data-testid="stMarkdownContainer"] {
            color: #2d2d2d !important;
        }

        .stChatInput > div {
            background: #fff !important;
            border: 2px solid #2d2d2d !important;
            border-radius: 5px !important;
        }

        .stChatInput input {
            color: #2d2d2d !important;
            font-family: 'Patrick Hand', cursive !important;
            font-size: 1rem !important;
        }

        .stChatInput input::placeholder {
            color: #888 !important;
        }

        .stTextInput > div > div > input {
            background: #fff !important;
            border: 2px solid #2d2d2d !important;
            border-radius: 3px !important;
            color: #2d2d2d !important;
            font-family: 'Patrick Hand', cursive !important;
        }

        .stSelectbox > div > div {
            background: #fff !important;
            border-radius: 3px !important;
            color: #2d2d2d !important;
            border: 2px solid #2d2d2d !important;
        }

        .stSelectbox label, .stTextInput label, .stTextArea label, .stSlider label {
            color: #2d2d2d !important;
            font-family: 'Patrick Hand', cursive !important;
            font-size: 1.1rem !important;
        }

        .stTextArea textarea {
            background: #fff !important;
            border: 2px solid #2d2d2d !important;
            border-radius: 3px !important;
            color: #2d2d2d !important;
            font-family: 'Patrick Hand', cursive !important;
        }

        p, span, label, div {
            color: #2d2d2d;
        }

        .stCaption, .stCaption p {
            color: #666 !important;
            font-family: 'Patrick Hand', cursive !important;
        }

        .stars {
            color: #2d2d2d;
            font-size: 0.9rem;
        }

        hr {
            border: none;
            border-top: 2px solid #2d2d2d;
            margin: 15px 0;
        }

        .stForm {
            background: transparent;
        }

        /* Slider */
        .stSlider > div > div > div {
            background: #2d2d2d !important;
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
    st.markdown('<h1 class="main-title">Mumbai Local ⚡</h1>', unsafe_allow_html=True)
    st.markdown('''<p class="subtitle">
        <span class="line-badge">Western</span>
        <span class="line-badge">Central</span>
        <span class="line-badge">Harbour</span>
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
                    "hey! welcome to mumbai local\n\n"
                    "i can help you with train timings, routes & more\n\n"
                    "**try asking:**\n"
                    "• andheri to churchgate\n"
                    "• ac trains on western line\n"
                    "• reviews for dadar\n"
                    "• monthly pass price"
                )
            }
        )

    # -------- Chat History --------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # -------- Chat Input --------
    user_input = st.chat_input("search trains, routes...")

    # -------- Suggested Queries --------
    st.markdown('<p class="section-header">try these →</p>', unsafe_allow_html=True)
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
                        response = f"**{station} station**\n" + review_summary
                    else:
                        response = f"no reviews for {station} yet! be the first to write one"
                    break
            else:
                response = "which station? try: *reviews for andheri*"
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
    st.markdown('<p class="section-header">write a review</p>', unsafe_allow_html=True)

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
    st.markdown('<p class="section-header">recent reviews</p>', unsafe_allow_html=True)

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
