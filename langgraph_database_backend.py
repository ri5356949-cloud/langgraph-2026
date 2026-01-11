from langgraph.graph import StateGraph,START,END
from typing import TypedDict,Annotated
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import sqlite3


load_dotenv()
llm = ChatOpenAI()

class chatstate(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

def chat_node(state:chatstate):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages":[response]}

conn =sqlite3.connect(database='chatbot.db',check_same_thread=False)


checkpoointer = SqliteSaver(conn=conn)

graph = StateGraph(chatstate)
graph.add_node("chat_node",chat_node)
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

chatbot = graph.compile(checkpointer=checkpoointer)

    
def retriew_all_threads():
    all_threads = set()
    for checkpoint in checkpoointer.list(None):  
        all_threads.add(checkpoint.config['configurable']['thread_id'])
    return list(all_threads)  