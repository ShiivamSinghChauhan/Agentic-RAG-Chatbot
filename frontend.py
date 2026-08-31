import streamlit as st
from backend import chatbot, retrieve_all_threads 
from langchain_core.messages import HumanMessage, AIMessage, AIMessageChunk
import uuid

# =================================== session state ====================================

if "threads" not in st.session_state:
    st.session_state["threads"] = retrieve_all_threads()

if "current_thread" not in st.session_state:
    st.session_state["current_thread"] = ''

# ================================= utility functions ==================================

def load_chats(thread_id):

    config = {"configurable": {"thread_id": thread_id}}
    thread_chats_data = chatbot.get_state(config).values

    if not thread_chats_data:
        return []

    messages = thread_chats_data.get("chat_history", [])

    conversation = [
        {"role": msg.type, "content": msg.content}
        for msg in messages
    ]

    return conversation

def show_chat_history(thread_id):
    conversation = load_chats(thread_id)
    for msg in conversation:
        with st.chat_message(msg["role"]):
            st.text(msg["content"])


def generate_new_thread():
    if st.session_state["threads"]:
        last_thread_id = st.session_state["threads"][-1]

        thread_chats_data = chatbot.get_state({"configurable": {"thread_id": last_thread_id}}).values
        if not thread_chats_data:
            return last_thread_id

    thread_id = str(uuid.uuid4())
    st.session_state["threads"].append(thread_id)

    return thread_id


# ===================================== Side bar UI ====================================

st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    st.session_state["current_thread"] = generate_new_thread()

st.sidebar.header("My conversation")

if st.session_state['threads']:
    for thread_id in st.session_state['threads'][::-1]:
        if st.sidebar.button(str(thread_id)):
            st.session_state['current_thread'] = thread_id
            # conversation = load_chats(thread_id)


# ======================================= Main UI ======================================

if not st.session_state["threads"]:
    st.session_state["current_thread"] = generate_new_thread()

# load past chats if any
conversation = load_chats(st.session_state["current_thread"])
show_chat_history(st.session_state['current_thread'])

# next chat
user_message = st.chat_input("Type Here")
if user_message:
    with st.chat_message("human"):
        st.text(user_message)

    input_state = {"chat_history":[HumanMessage(content=user_message)]}
    config = {"configurable":{"thread_id":st.session_state["current_thread"]}}

    ai_message = st.write_stream(
        message_chunk.content for message_chunk, metadata in chatbot.stream(
            input_state, 
            config=config,
            stream_mode="messages"
        ) if isinstance(message_chunk, AIMessageChunk)
    )
