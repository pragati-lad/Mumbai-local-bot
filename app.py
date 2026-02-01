import streamlit as st
from train_chatbot_enhanced import chatbot_response

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Mumbai Local Train Assistant",
    page_icon="🚆",
    layout="centered"
)

# ---------------- CSS (KEEP OLD DESIGN) ----------------
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
            color: #9ca3af;
            font-size: 0.9rem;
            margin-bottom: 1rem;
        }

        .stButton > button {
            background-color: #ffffff !important;
            border: 1px solid #e5e7eb !important;
            color: #111827 !important;
            border-radius: 999px;
            padding: 0.45rem 0.9rem;
            font-size: 0.82rem;
            text-align: left;
            width: 100%;
        }

        .stButton > button:hover {
            background-color: #f3f4f6 !important;
            border-color: #d1d5db !important;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- Header ----------------
st.markdown("<div class='header-title'>Mumbai Local Train Assistant</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='header-subtitle'>Routes • Timetables • Passes • Railway rules</div>",
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
                "Hello 👋 I’m the **Mumbai Local Train Assistant**.\n\n"
                "Ask me about routes, passes, concessions, luggage rules or timetables."
            )
        }
    )

# ---------------- Chat Input (TOP) ----------------
user_input = st.chat_input("Ask about Mumbai local trains...")

# ---------------- Suggested Queries (JUST BELOW INPUT) ----------------
st.markdown("**Suggested queries**")

cols = st.columns(2)
for i, q in enumerate(st.session_state.suggestions):
    if cols[i % 2].button(q, key=f"sugg_{i}"):
        st.session_state.pending_query = q

# 🔥 Auto-run when suggestion clicked
if st.session_state.pending_query:
    user_input = st.session_state.pending_query
    st.session_state.pending_query = None

# ---------------- Chat History ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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
