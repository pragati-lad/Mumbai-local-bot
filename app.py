import streamlit as st
from train_chatbot_enhanced import chatbot_response

st.set_page_config(
    page_title="Mumbai Local Train Assistant",
    page_icon="🚆",
    layout="centered"
)

st.markdown(
    "<h2 style='text-align:center'>Mumbai Local Train Assistant</h2>"
    "<p style='text-align:center;color:gray'>Routes • Timetables • Railway Rules</p>",
    unsafe_allow_html=True
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if len(st.session_state.messages) == 0:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "Hello 👋 Ask me about routes, timetables, or railway rules."
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input("Ask about Mumbai local trains")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.markdown(user_input)

    response = chatbot_response(user_input)

    with st.chat_message("assistant"):
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
