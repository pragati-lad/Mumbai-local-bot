import streamlit as st
from train_chatbot_enhanced import chatbot_response


# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Mumbai Local Train Assistant",
    page_icon="🚆",
    layout="centered"
)

# ---------------- CSS ----------------
st.markdown(
    """
    <style>
        body {
            background-color: #f9fafb;
            color: #111827;
        }

        .header-title {
            text-align: center;
            font-size: 1.4rem;
            font-weight: 600;
            color: #111827;
        }

        .header-subtitle {
            text-align: center;
            color: #6b7280;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }

        /* 🔥 FIX FOR SUGGESTED QUERY BUTTONS */
        .stButton > button {
            background-color: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            color: #1f2937 !important;   /* <-- TEXT COLOR FIX */
            border-radius: 999px;
            padding: 0.45rem 0.9rem;
            font-size: 0.82rem;
            text-align: left;
        }

        .stButton > button:hover {
            background-color: #f3f4f6 !important;
            border-color: #d1d5db !important;
            color: #111827 !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ---------------- Header ----------------
st.markdown("<div class='header-title'>Mumbai Local Train Assistant</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='header-subtitle'>Timetables, routes, and railway rules — simplified</div>",
    unsafe_allow_html=True
)

# ---------------- Session State ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "suggestions" not in st.session_state:
    st.session_state.suggestions = [
        "Train from Virar to Churchgate after 8 AM",
        "Harbour line trains from Panvel to CSMT",
        "What concessions are available for students?",
        "Luggage rules in Mumbai local trains",
    ]

# ---------------- Initial Bot Message ----------------
if len(st.session_state.messages) == 0:
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": (
                "Hello. I’m the **Mumbai Local Train Assistant**.\n\n"
                "Ask me about train timings, routes, or railway rules."
            )
        }
    )

# ---------------- Chat History ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- Suggested Queries (ALWAYS visible) ----------------
st.markdown("**Suggested queries**")

cols = st.columns(2)
for i, s in enumerate(st.session_state.suggestions):
    if cols[i % 2].button(s, key=f"sugg_{i}"):
        st.session_state.pending_input = s

# ---------------- Chat Input ----------------
user_input = st.chat_input("Ask about train timings, routes, or railway rules")

if "pending_input" in st.session_state:
    user_input = st.session_state.pending_input
    del st.session_state.pending_input

# ---------------- Suggestion Generator ----------------
def update_suggestions(query: str):
    q = query.lower()

    if any(x in q for x in ["panvel", "csmt", "harbour"]):
        return [
            "Next train from Panvel to CSMT",
            "First harbour line train tomorrow",
            "Train from Vashi to Kurla",
            "Harbour line timetable",
        ]

    if any(x in q for x in ["virar", "borivali", "western"]):
        return [
            "Next train from Virar to Churchgate",
            "AC trains on Western line",
            "Borivali to Andheri trains",
            "Western line timetable",
        ]

    if any(x in q for x in ["concession", "student", "senior"]):
        return [
            "Student concession documents required",
            "Senior citizen eligibility",
            "Disabled person concession",
            "Monthly pass discount rules",
        ]

    if any(x in q for x in ["refund", "cancel"]):
        return [
            "Online ticket cancellation rules",
            "Season ticket refund policy",
            "Refund for unused ticket",
            "How long does refund take?",
        ]

    return [
        "Train from Panvel to CSMT",
        "Western line timetable",
        "Railway concession rules",
        "Luggage allowance in local trains",
    ]

# ---------------- Handle Input ----------------
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = chatbot_response(user_input)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

    # 🔥 Update suggestions dynamically
    st.session_state.suggestions = update_suggestions(user_input)
