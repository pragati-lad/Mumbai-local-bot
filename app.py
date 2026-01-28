import streamlit as st
from train_chatbot_enhanced import chatbot_response

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Mumbai Local Train Assistant",
    page_icon="🚆",
    layout="centered"
)

# ---------------- Custom CSS ----------------
st.markdown(
    """
    <style>
        body {
            background-color: #0e1117;
            color: #e5e7eb;
        }
        .main {
            padding-top: 1.5rem;
        }
        h1, h2 {
            font-weight: 600;
        }
        .subtitle {
            color: #9ca3af;
            font-size: 0.95rem;
            text-align: center;
            margin-bottom: 1.5rem;
        }
        .stButton > button {
            background-color: #111827;
            border: 1px solid #374151;
            color: #e5e7eb;
            border-radius: 10px;
            padding: 0.6rem 0.9rem;
            font-size: 0.85rem;
            text-align: left;
        }
        .stButton > button:hover {
            background-color: #1f2937;
            border-color: #4b5563;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Header ----------------
st.markdown(
    "<h2 style='text-align:center;'>Mumbai Local Train Assistant</h2>",
    unsafe_allow_html=True
)
st.markdown(
    "<div class='subtitle'>Timetables, routes, and railway rules — simplified</div>",
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
                "You can start by selecting a suggested query below or typing your own."
            )
        }
    )

# ---------------- Suggested Queries ----------------
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
for i, query in enumerate(suggested_queries):
    if cols[i % 2].button(query):
        st.session_state.selected_prompt = query

st.divider()

# ---------------- Chat History ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- Chat Input ----------------
user_input = st.chat_input(
    "Ask about train timings, routes, or railway rules"
)

# If user clicks a suggested query
if st.session_state.selected_prompt:
    user_input = st.session_state.selected_prompt
    st.session_state.selected_prompt = None

# ---------------- Handle User Input ----------------
if user_input:
    # User message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant response
    with st.chat_message("assistant"):
        response = chatbot_response(user_input)
        st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
