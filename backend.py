from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, AnyMessage
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated
from dotenv import load_dotenv
import sqlite3

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-20b", streaming=True)

class ChatState(TypedDict):
    chat_history: Annotated[list[AnyMessage], add_messages]

def chat_node(state: ChatState)->ChatState:
    chats = state["chat_history"]
    response = llm.invoke(chats)
    
    return {"chat_history": [response]}


conn = sqlite3.connect(database="chatbot.db", check_same_thread=False)
checkpointer = SqliteSaver(conn=conn)
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    return list(set([i.config["configurable"]["thread_id"] for i in checkpointer.list(None)]))
