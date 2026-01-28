import streamlit as st
from train_chatbot_enhanced import chatbot_response

# ---------- Page Config ----------
st.set_page_config(
    page_title="Mumbai Local Bot",
    page_icon="🚆",
    layout="centered"
)

# ---------- Custom CSS (Clean & Minimal) ----------
st.markdown(
    """
    <style>
        body {
            background-color: #fafafa;
        }
        .main {
            padding-top: 2rem;
        }
        h1, h2, h3 {
            font-weight: 600;
        }
        .subtitle {
            color: #6b7280;
            font-size: 0.95rem;
            text-align: center;
            margin-bottom: 2rem;
        }
        .example-btn {
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 0.6rem;
            background-color: white;
            color: #111827;
            font-size: 0.85rem;
        }
        .example-btn:hover {
            background-color: #f9fafb;
            border-color: #d1d5db;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Header ----------
st.markdown("<h2 style='text-align:center;'>Mumbai Local Train Assistant</h2>", unsafe_allow_html=True)
st.markdown(
    "<div class='subtitle'>Timetables, routes, and railway rules — simplified</div>",
    unsafe_allow_html=True
)

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_example" not in st.session_state:
    st.session_state.selected_example = None

# ---------- Example Questions ----------
st.markdown("**Example questions**")

examples = [
    "Train from Virar to Churchgate after 8 AM",
    "Harbour line trains from Panvel to CSMT",
    "What concessions are available for students?",
    "Senior citizen discount rules",
    "Luggage rules in Mumbai local trains",
    "How can I get a ticket refund?"
]

cols = st.columns(2)
for i, ex in enumerate(examples):
    if cols[i % 2].button(ex, key=ex):
        st.session_state.selected_example = ex

st.divider()

# ---------- Chat History ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Input ----------
user_input = st.chat_input("Ask a question about Mumbai local trains")

if st.session_state.selected_example:
    user_input = st.session_state.selected_example
    st.session_state.selected_example = None

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
