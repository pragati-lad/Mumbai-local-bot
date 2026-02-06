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
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Header ----------------
st.title("Mumbai Local Train Assistant")
st.caption("Timetables, routes, passes & railway rules")

# ---------------- Session State ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "suggestions" not in st.session_state:
    st.session_state.suggestions = [
        "Andheri to Churchgate",
        "Thane to CSMT",
        "Dadar to Kalyan",
        "Kurla to Panvel",
        "AC trains on Western line",
        "Monthly pass price",
        "Student concession",
        "Luggage rules",
    ]

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
                "• **Info**: \"Monthly pass price\" or \"Luggage rules\""
            )
        }
    )

# ==================================================
# ✅ 1. CHAT HISTORY (TOP)
# ==================================================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ==================================================
# ✅ 2. CHAT INPUT (MIDDLE)
# ==================================================
user_input = st.chat_input("Ask about Mumbai local trains...")

# ==================================================
# ✅ 3. SUGGESTED QUERIES (BELOW INPUT)
# ==================================================
st.markdown("### Suggested queries")
cols = st.columns(2)
for i, s in enumerate(st.session_state.suggestions):
    if cols[i % 2].button(s, key=f"sugg_{i}"):
        user_input = s

# ==================================================
# HANDLE INPUT
# ==================================================
if user_input:
    # User message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Assistant response
    response = chatbot_response(user_input)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
