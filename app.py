import streamlit as st
from train_chatbot_enhanced import chatbot_response

st.set_page_config(
    page_title="Mumbai Local Train Assistant",
    page_icon="🚆",
    layout="centered"
)

# ---------- Header ----------
st.title("Mumbai Local Train Assistant")
st.caption("Timetables, routes, passes & railway rules")

# ---------- Search bar (THIS replaces chat_input) ----------
query = st.text_input(
    "",
    placeholder="Ask about Mumbai local trains…",
)

# ---------- Suggested queries BELOW search bar ----------
st.markdown("### Suggested queries")

suggestions = [
    "Dadar to Churchgate",
    "Sion to Grant Road",
    "Western line timetable",
    "Monthly pass price",
    "Student concession documents",
    "Luggage rules in local trains",
    "AC trains on Western line",
]

cols = st.columns(2)
for i, s in enumerate(suggestions):
    if cols[i % 2].button(s):
        query = s

st.divider()

# ---------- Response ----------
if query:
    with st.spinner("Processing…"):
        response = chatbot_response(query)
    st.markdown(response)
