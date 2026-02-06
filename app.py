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
        "AC trains on Western line",
        "Monthly pass price",
        "Student concession",
        "Luggage rules",
    ],
    "western": [
        "Bandra to Virar",
        "Borivali to Churchgate",
        "Dadar to Andheri",
        "Churchgate to Borivali",
        "AC trains on Western line",
        "Reviews for Andheri Station",
    ],
    "central": [
        "CSMT to Kalyan",
        "Thane to Dadar",
        "Ghatkopar to CSMT",
        "Kurla to Thane",
        "Dadar to Dombivli",
        "Reviews for Thane Station",
    ],
    "harbour": [
        "CSMT to Panvel",
        "Vashi to CSMT",
        "Kurla to Vashi",
        "Panvel to Kurla",
        "Belapur to CSMT",
        "Reviews for Vashi Station",
    ],
    "ac": [
        "AC trains on Western line",
        "AC trains on Central line",
        "AC trains from Churchgate",
        "AC trains from Virar",
        "AC trains",
        "Monthly pass price",
    ],
    "info": [
        "Monthly pass price",
        "Student concession",
        "Senior citizen concession",
        "Luggage rules",
        "AC trains",
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

    # Check for AC trains
    if "ac" in q or "air condition" in q:
        return SUGGESTIONS["ac"]

    # Check for info queries
    if any(word in q for word in ["pass", "concession", "student", "senior", "luggage", "rule"]):
        return SUGGESTIONS["info"]

    # Check for Western line stations
    western_stations = ["churchgate", "bandra", "andheri", "borivali", "virar", "dadar", "malad", "goregaon"]
    if any(station in q for station in western_stations):
        central_stations = ["csmt", "cst", "thane", "kalyan", "ghatkopar", "dombivli"]
        harbour_stations = ["panvel", "vashi", "belapur"]
        if not any(s in q for s in central_stations + harbour_stations):
            return SUGGESTIONS["western"]

    # Check for Central line stations
    central_stations = ["csmt", "cst", "thane", "kalyan", "ghatkopar", "kurla", "dombivli", "mulund"]
    if any(station in q for station in central_stations):
        harbour_stations = ["panvel", "vashi", "belapur"]
        if not any(s in q for s in harbour_stations):
            return SUGGESTIONS["central"]

    # Check for Harbour line stations
    harbour_stations = ["panvel", "vashi", "belapur", "nerul", "sanpada"]
    if any(station in q for station in harbour_stations):
        return SUGGESTIONS["harbour"]

    return SUGGESTIONS["default"]


# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Mumbai Local Train Assistant",
    page_icon="🚆",
    layout="wide"
)

# ---------------- CSS ----------------
st.markdown(
    """
    <style>
        .stButton > button {
            background-color: #111827 !important;
            border: 1px solid #374151 !important;
            color: #f9fafb !important;
            border-radius: 999px;
            padding: 0.45rem 0.9rem;
            font-size: 0.82rem;
        }
        .stButton > button:hover {
            background-color: #1f2937 !important;
        }
        .review-card {
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 8px;
            margin: 5px 0;
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
    st.title("🚆 Mumbai Local Train Assistant")
    st.caption("7,500+ real train schedules • Reviews • Routes • Info")

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
                    "Hello 👋 I'm the **Mumbai Local Train Assistant**.\n\n"
                    "I have **7,500+ real train schedules** across Western, Central & Harbour lines.\n\n"
                    "Try asking:\n"
                    "• **Train times**: \"Andheri to Churchgate\"\n"
                    "• **AC locals**: \"AC trains on Western line\"\n"
                    "• **Reviews**: \"Reviews for Dadar Station\"\n"
                    "• **Info**: \"Monthly pass price\""
                )
            }
        )

    # -------- Chat History --------
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # -------- Chat Input --------
    user_input = st.chat_input("Ask about trains, stations, or reviews...")

    # -------- Suggested Queries --------
    st.markdown("### 💡 Suggested queries")
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
        if "review" in user_input.lower():
            # Extract station/route from query
            for station in STATIONS:
                if station.lower() in user_input.lower():
                    review_summary = get_review_summary(station)
                    if review_summary:
                        response = f"📍 **{station} Station**\n" + review_summary
                    else:
                        response = f"No reviews yet for {station}. Be the first to add one! 👉"
                    break
            else:
                response = "Which station would you like reviews for? Try: \"Reviews for Andheri Station\""
        else:
            # Regular chatbot response
            response = chatbot_response(user_input)

            # Add review summary if query mentions a station
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
    st.markdown("### ✍️ Share Your Experience")

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

        review_rating = st.slider("Rating", 1, 5, 4, format="%d ⭐")

        review_comment = st.text_area(
            "Your Review",
            placeholder="Share your experience... (crowd, cleanliness, timing, etc.)",
            max_chars=500
        )

        review_name = st.text_input("Name (optional)", placeholder="Anonymous")

        submitted = st.form_submit_button("Submit Review", use_container_width=True)

        if submitted and review_comment:
            add_user_review(
                category=review_category.lower(),
                subject=review_subject,
                rating=review_rating,
                comment=review_comment,
                username=review_name if review_name else "Anonymous"
            )
            st.success("✅ Thank you for your review!")
            st.rerun()

    # Recent Reviews
    st.markdown("---")
    st.markdown("### 📝 Recent Reviews")

    reviews_list = get_all_reviews_from_sheets()

    if reviews_list:
        # Show latest 5 reviews
        for review in reversed(reviews_list[-5:]):
            stars = "⭐" * review.get("rating", 0)
            st.markdown(f"""
            <div class="review-card">
                <b>{review.get('subject', 'Unknown')}</b> {stars}<br>
                <small>{review.get('comment', '')[:150]}</small><br>
                <small style="color: gray;">— {review.get('username', 'Anonymous')}</small>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No reviews yet. Be the first to share your experience!")

    # Stats
    st.markdown("---")
    st.markdown("### 📊 Stats")
    total_reviews = len(reviews_list)
    st.metric("Total Reviews", total_reviews)

    # Connection status
    connection = check_sheets_connection()
    if connection['connected']:
        st.caption("☁️ Synced to Google Sheets")
    else:
        st.caption("💾 Local storage (reviews may reset)")
