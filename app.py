import streamlit as st
from train_chatbot_enhanced import chatbot_response

# ---------------- Page Config ----------------
st.set_page_config(
    page_title="Mumbai Local Train Assistant",
    page_icon="🚆",
    layout="centered"
)

# ---------------- Header ----------------
st.markdown("## Mumbai Local Train Assistant")
st.caption("Routes • Concessions • Luggage • Pass rules")

# ---------------- Session State ----------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "suggestions" not in st.session_state:
    st.session_state.suggestions = [
        "Sion to Grant Road",
        "Dadar to Churchgate",
        "Virar to Andheri",
        "Student concession",
        "Senior citizen concession",
        "Luggage rules",
        "Monthly pass price",
    ]

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

# ---------------- Chat Input ----------------
user_input = st.chat_input(
    "Ask about routes, concessions, luggage, passes",
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
