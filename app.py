import streamlit as st
from train_chatbot_enhanced import chatbot_response

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Mumbai Local Train Assistant",
    page_icon="🚆",
    layout="centered"
)

# ---------------- Custom CSS (Light & Professional) ----------------
st.markdown(
    """
    <style>
        body {
            background-color: #64798f;
            color: #a1c2d1;
        }
        .main {
            padding-top: 1.2rem;
        }
        .header-title {
            text-align: center;
            font-size: 1.4rem;
            font-weight: 600;
            color: #a1c2d1;
        }
        .header-subtitle {
            text-align: center;
            color: #6b7280;
            font-size: 0.9rem;
            margin-bottom: 1.2rem;
        }
        .stButton > button {
            background-color: #ffffff;
            border: 1px solid #e5e7eb;
            color: #111827;
            border-radius: 999px;
            padding: 0.45rem 0.9rem;
            font-size: 0.82rem;
            text-align: left;
        }
        .stButton > button:hover {
            background-color: #f3f4f6;
            border-color: #d1d5db;
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

if "selected_prompt" not in st.session_state:
    st.session_state.selected_prompt = None

# ---------------- Initial Bot Message ----------------
if len(st.session_state.messages) == 0:
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": (
                "Hello. I’m the **Mumbai Local Train Assistant**.\n\n"
                "I can help you with:\n"
                "- Local train timings (Western & Harbour lines)\n"
                "- Routes and station information\n"
                "- Railway rules, concessions, and refunds\n\n"
                "Select a suggested query below or type your own question."
            )
        }
    )

# ---------------- Chat History ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- Suggested Queries (Only at start) ----------------
if len(st.session_state.messages) == 1:
    st.markdown("**Suggested queries**")

    suggested_queries = [
        "Train from Virar to Churchgate after 8 AM",
        "Harbour line trains from Panvel to CSMT",
        "What concessions are available for students?",
        "Senior citizen discount rules",
        "Luggage rules in Mumbai local trains",
        "How can I get a ticket refund?"
    ]

    cols = st.columns(2)
    for i, q in enumerate(suggested_queries):
        if cols[i % 2].button(q):
            st.session_state.selected_prompt = q

# ---------------- Chat Input ----------------
user_input = st.chat_input(
    "Ask about train timings, routes, or railway rules"
)

if st.session_state.selected_prompt:
    user_input = st.session_state.selected_prompt
    st.session_state.selected_prompt = None

# ---------------- Handle User Input ----------------
if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = chatbot_response(user_input)
        st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
