import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

# ---------- Utility Functions ----------
def generate_thread_id():
    return str(uuid.uuid4())

def reset_chat():
    st.session_state["thread_id"] = generate_thread_id()
    st.session_state["message_history"] = []
    add_thread(st.session_state["thread_id"])

def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)

def load_conversation(thread_id):
    return chatbot.get_state(
        config={"configurable": {"thread_id": thread_id}}
    ).values.get("messages", [])

# ---------- Session Setup ----------
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = []

add_thread(st.session_state["thread_id"])

# ---------- Sidebar (ChatGPT Style) ----------
st.sidebar.title("LangGraph Chatbot 🤖")

if st.sidebar.button("➕ New Chat"):
    reset_chat()

st.sidebar.subheader("Your chats")

# latest chat on top
for thread_id in reversed(st.session_state["chat_threads"]):

    messages = load_conversation(thread_id)

    # default title
    title = "New Chat"

    # first user message as title
    for msg in messages:
        if isinstance(msg, HumanMessage):
            title = msg.content[:30]
            break

    if st.sidebar.button(title, key=thread_id):
        st.session_state["thread_id"] = thread_id

        temp_messages = []
        for msg in messages:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            temp_messages.append({
                "role": role,
                "content": msg.content
            })

        st.session_state["message_history"] = temp_messages

# ---------- Display Old Messages ----------
for msg in st.session_state["message_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------- User Input ----------
user_input = st.chat_input("Type your message...")

if user_input:
    # Save & show user message
    st.session_state["message_history"].append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    CONFIG = {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        }
    }

    # ---------- Assistant Streaming Response ----------
    assistant_reply = ""

    with st.chat_message("assistant"):
        placeholder = st.empty()

        for message_chunk, metadata in chatbot.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=CONFIG,
            stream_mode="messages"
        ):
            assistant_reply += message_chunk.content
            placeholder.markdown(assistant_reply)

    # Save assistant message
    st.session_state["message_history"].append({
        "role": "assistant",
        "content": assistant_reply
    })
