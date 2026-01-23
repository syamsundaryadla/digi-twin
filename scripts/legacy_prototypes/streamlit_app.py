import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(
    page_title="RepliMate",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 RepliMate")
st.caption("Personalized AI Assistant (RAG powered)")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Ask something about the user...")

if user_input:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call FastAPI
    response = requests.post(
        API_URL,
        json={"question": user_input}
    )

    if response.status_code == 200:
        answer = response.json()["answer"]
    else:
        answer = "❌ Error connecting to AI backend."

    # Show assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": answer}
    )
    with st.chat_message("assistant"):
        st.markdown(answer)
