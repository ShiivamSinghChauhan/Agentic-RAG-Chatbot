import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage, AIMessageChunk

# =========================================== Sidebar UI ==================================================

st.sidebar.title("LangGraph Chatbot")
st.sidebar.button("New Chat")
st.sidebar.header("My Conversations")

# ============================================= Main UI ===================================================

thread_id = 'thread-1'

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [] # [{'role':"", 'content':""}, ...]

if st.session_state["chat_history"]:
    for message in st.session_state["chat_history"]:
        with st.chat_message(message["role"]):
            st.text(message["content"])

user_message = st.chat_input("Type Here")

if user_message:
    # first append the user message in chat_history
    st.session_state["chat_history"].append({"role":"user", "content":user_message})
    # now show the user message
    with st.chat_message("user"):
        st.text(user_message)

    input_state = {"chat_history":[HumanMessage(content=user_message)]}
    config = {"configurable":{"thread_id":thread_id}}

# -------------------------------------------------------------------------------------------------------
    # result = chatbot.invoke(input_state, config=config)
    # response = result["chat_history"][-1].content
    # # first append the ai message in chat_history
    # st.session_state["chat_history"].append({"role":"assistant", "content":response})
    # # now show ai response
    # with st.chat_message("assistant"):
    #     st.text(response ) 
# -------------------------------------------------------------------------------------------------------
    ai_message = st.write_stream(
        message_chunk.content for message_chunk, metadata in chatbot.stream(
            input_state, 
            config=config,
            stream_mode="messages"
        ) if isinstance(message_chunk, AIMessageChunk)
    )
    st.session_state["chat_history"].append({'role':'assistant', "content":ai_message})
