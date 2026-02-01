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
    body { background-color: #f9fafb; }
    .title { text-align:center; font-size:1.4rem; font-weight:600; }
    .subtitle { text-align:center; color:#6b7280; font-size:0.9rem; }
    .stButton>button {
        background:#fff;
        border:1px solid #e5e7eb;
        border-radius:999px;
        color:#111827;
        font-size:0.82rem;
        padding:0.45rem 0.9rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Header ----------------
st.markdown("<div class='title'>Mumbai Local Train Assistant</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Routes • Timetables • Railway rules</div>", unsafe_allow_html=True)

# ---------------- Session State ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "suggestions" not in st.session_state:
    st.session_state.suggestions = [
        "Sion to Grant Road",
        "Dadar to Churchgate",
        "Virar to Andheri",
        "Western line timetable",
    ]

# ---------------- Suggestion Click Handler (🔥 FIX) ----------------
def handle_suggestion_click(text):
    st.session_state.chat_input = text

# ---------------- Chat History ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- Suggested Queries ----------------
st.markdown("**Suggested queries**")
cols = st.columns(2)

for i, s in enumerate(st.session_state.suggestions):
    cols[i % 2].button(
        s,
        key=f"sugg_{i}",
        on_click=handle_suggestion_click,
        args=(s,)
    )

# ---------------- Chat Input (FIXED) ----------------
user_input = st.chat_input(
    "Ask about routes, stations, or railway rules",
    key="chat_input"
)

# ---------------- Handle Input ----------------
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        response = chatbot_response(user_input)
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
