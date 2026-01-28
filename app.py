import streamlit as st
from train_chatbot_enhanced import chatbot_response

st.set_page_config(page_title="Mumbai Train Chatbot", page_icon="🚂")

st.title("🚂 Mumbai Train Timetable Chatbot")
st.write("Ask about train timings or railway rules")

user_input = st.text_input(
    "Your Question",
    placeholder="e.g. Train from Virar to Churchgate or student concession"
)

if user_input:
    reply = chatbot_response(user_input)
    st.markdown(reply)
