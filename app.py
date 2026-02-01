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
        .header-title {
            text-align: center;
            font-size: 1.4rem;
            font-weight: 600;
        }
        .header-subtitle {
            text-align: center;
            color: #6b7280;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }
        .stButton > button {
            background-color: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            color: #1f2937 !important;
            border-radius: 999px;
            padding: 0.45rem 0.9rem;
            font-size: 0.82rem;
            text-align: left;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Header ----------------
st.markdown("<div class='header-title'>Mumbai Local Train Assistant</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='header-subtitle'>Timetables, routes, passes & railway rules</div>",
    unsafe_allow_html=True
)

# ---------------- Session State ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "suggestions" not in st.session_state:
    st.session_state.suggestions = [
        "Dadar to Churchgate",
        "Sion to Grant Road",
        "Western line timetable",
        "Monthly pass price",
        "Student concession documents",
        "Luggage rules in local trains",
        "AC trains on Western line",
    ]

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

# ---------------- Initial Bot Message ----------------
if not st.session_state.messages:
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": (
                "Hi 👋 I’m the **Mumbai Local Train Assistant**.\n\n"
                "Ask me about routes, passes, concessions, luggage rules or timetables."
            )
        }
    )

# ---------------- Chat History ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- Suggested Queries (BELOW CHAT INPUT) ----------------
st.markdown("**Suggested queries**")
cols = st.columns(2)

for i, q in enumerate(st.session_state.suggestions):
    if cols[i % 2].button(q, key=f"suggest_{i}"):
        st.session_state.pending_query = q

# ---------------- Chat Input ----------------
user_input = st.chat_input("Ask about Mumbai local trains...")

# 🔥 If suggestion clicked → auto execute
if st.session_state.pending_query:
    user_input = st.session_state.pending_query
    st.session_state.pending_query = None

# ---------------- Handle Input ----------------
if user_input:
    # User message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Bot response
    response = chatbot_response(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        st.markdown(response)
