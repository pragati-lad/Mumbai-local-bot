import streamlit as st
from train_chatbot_enhanced import chatbot_response

# ---------- Page Config ----------
st.set_page_config(
    page_title="Mumbai Local Train Bot",
    page_icon="🚆",
    layout="centered"
)

# ---------- Sidebar ----------
with st.sidebar:
    st.title("🚆 Mumbai Local Bot")
    st.markdown(
        """
        **Ask me about:**
        - 🚉 Train timings  
        - 🔵 Western & 🟢 Harbour lines  
        - 🎓 Concessions & 💰 refunds  
        - 🧳 Luggage rules  

        Click an example or type your own question.
        """
    )
    #st.divider()
    #st.caption("Deployed on Streamlit Cloud")

# ---------- Main Header ----------
st.markdown(
    "<h2 style='text-align: center;'>🤖 Mumbai Local Train Chatbot</h2>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align: center; color: gray;'>Your smart assistant for Mumbai local trains</p>",
    unsafe_allow_html=True
)

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_example" not in st.session_state:
    st.session_state.selected_example = None

# ---------- Example Questions ----------
st.markdown("### 💡 Try these example questions:")

examples = [
    "Train from Virar to Churchgate after 8 AM",
    "Harbour line train from Panvel to CSMT",
    "What are student concessions?",
    "Senior citizen discount rules",
    "Luggage rules in local trains",
    "How to get ticket refund?",
]

cols = st.columns(2)
for i, example in enumerate(examples):
    if cols[i % 2].button(example):
        st.session_state.selected_example = example

# ---------- Display Chat History ----------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- Chat Input ----------
user_input = st.chat_input("Type your question here…")

# If user clicks an example, treat it as input
if st.session_state.selected_example:
    user_input = st.session_state.selected_example
    st.session_state.selected_example = None

if user_input:
    # User message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Bot response
    with st.chat_message("assistant"):
        with st.spinner("Finding trains 🚆..."):
            response = chatbot_response(user_input)
            st.markdown(response)

    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )
