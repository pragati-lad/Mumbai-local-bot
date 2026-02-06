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

# ---------------- CSS - Bubbly Mumbai Theme ----------------
# Warm faded tones: sunset orange, sea blue, cream, soft corals
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&display=swap');

        .stApp {
            background: linear-gradient(135deg,
                #fff5eb 0%,
                #ffecd2 25%,
                #fcb69f 50%,
                #ffecd2 75%,
                #d4f1f9 100%);
            background-attachment: fixed;
            font-family: 'Nunito', sans-serif;
        }

        .main-title {
            color: #2d3436;
            font-size: 2.4rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 5px;
        }

        .title-accent {
            background: linear-gradient(90deg, #e17055, #fdcb6e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .subtitle {
            color: #636e72;
            text-align: center;
            font-size: 0.95rem;
            margin-bottom: 1rem;
        }

        .line-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            margin: 0 3px;
        }
        .western { background: rgba(116, 185, 255, 0.3); color: #0984e3; }
        .central { background: rgba(255, 118, 117, 0.3); color: #d63031; }
        .harbour { background: rgba(85, 239, 196, 0.3); color: #00b894; }

        .stButton > button {
            background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%) !important;
            border: none !important;
            color: white !important;
            border-radius: 25px;
            padding: 0.5rem 1.2rem;
            font-size: 0.85rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(253, 121, 168, 0.3);
        }

        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(253, 121, 168, 0.4);
        }

        .review-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            padding: 14px 16px;
            border-radius: 16px;
            margin: 10px 0;
            border: 1px solid rgba(255, 255, 255, 0.5);
            box-shadow: 0 4px 20px rgba(0,0,0,0.05);
        }

        .review-card b {
            color: #2d3436;
            font-weight: 700;
        }

        .review-card small {
            color: #636e72;
        }

        .section-header {
            color: #2d3436;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }

        /* Chat styling */
        .stChatMessage {
            background: rgba(255, 255, 255, 0.6) !important;
            backdrop-filter: blur(10px) !important;
            border-radius: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.5) !important;
        }

        div[data-testid="stMarkdownContainer"] p {
            color: #2d3436 !important;
        }

        div[data-testid="stMarkdownContainer"] {
            color: #2d3436 !important;
        }

        .stChatInput > div {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 25px !important;
            border: 1px solid rgba(0,0,0,0.15) !important;
        }

        .stChatInput input {
            color: #2d3436 !important;
        }

        .stTextInput > div > div > input {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(0,0,0,0.15) !important;
            border-radius: 12px !important;
            color: #2d3436 !important;
        }

        .stSelectbox > div > div {
            background: rgba(255, 255, 255, 0.9) !important;
            border-radius: 12px !important;
            color: #2d3436 !important;
        }

        .stSelectbox label, .stTextInput label, .stTextArea label, .stSlider label {
            color: #2d3436 !important;
        }

        .stTextArea textarea {
            background: rgba(255, 255, 255, 0.9) !important;
            border: 1px solid rgba(0,0,0,0.15) !important;
            border-radius: 12px !important;
            color: #2d3436 !important;
        }

        /* All text elements */
        p, span, label, div {
            color: #2d3436;
        }

        .stCaption, .stCaption p {
            color: #636e72 !important;
        }

        .stSlider > div > div > div {
            background: linear-gradient(90deg, #fd79a8, #fdcb6e) !important;
        }

        .stars {
            color: #fdcb6e;
        }

        /* Glass card effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 20px;
            border: 1px solid rgba(255, 255, 255, 0.5);
        }

        /* Form styling */
        .stForm {
            background: rgba(255, 255, 255, 0.5);
            border-radius: 20px;
            padding: 10px;
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
    st.markdown('<h1 class="main-title">Mumbai <span class="title-accent">Local</span> 🚊</h1>', unsafe_allow_html=True)
    st.markdown('''<p class="subtitle">
        <span class="line-badge western">Western</span>
        <span class="line-badge central">Central</span>
        <span class="line-badge harbour">Harbour</span>
        <br>7,500+ real train schedules
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
                    "Hey there! 👋 Welcome to Mumbai Local!\n\n"
                    "I can help you with train timings, routes & more.\n\n"
                    "**Try asking:**\n"
                    "• Andheri to Churchgate\n"
                    "• AC trains on Western line\n"
                    "• Reviews for Dadar station\n"
                    "• Monthly pass price"
                )
            }
        )

    # -------- Chat History --------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # -------- Chat Input --------
    user_input = st.chat_input("Where are you headed? 🚃")

    # -------- Suggested Queries --------
    st.markdown('<p class="section-header">✨ Popular searches</p>', unsafe_allow_html=True)
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
                        response = f"📍 **{station} Station**\n" + review_summary
                    else:
                        response = f"No reviews for {station} yet! Be the first to share your experience 💬"
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
    st.markdown('<p class="section-header">💬 Share your experience</p>', unsafe_allow_html=True)

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

        submitted = st.form_submit_button("Submit ✨", use_container_width=True)

        if submitted and review_comment:
            add_user_review(
                category=review_category.lower(),
                subject=review_subject,
                rating=review_rating,
                comment=review_comment,
                username=review_name if review_name else "Anonymous"
            )
            st.success("Thanks for sharing! 🎉")
            st.rerun()

    # Recent Reviews - ONLY user submitted reviews
    st.markdown("---")
    st.markdown('<p class="section-header">🔥 Recent reviews</p>', unsafe_allow_html=True)

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
        <div class="review-card" style="text-align: center; color: #636e72;">
            No reviews yet!<br>
            <small>Be the first to share ☝️</small>
        </div>
        """, unsafe_allow_html=True)

    # Connection status
    st.markdown("---")
    connection = check_sheets_connection()
    if connection['connected']:
        st.caption("☁️ Synced to cloud")
    else:
        st.caption("💾 Local mode")
