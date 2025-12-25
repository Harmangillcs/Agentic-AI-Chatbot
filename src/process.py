import sqlite3
from langgraph.graph import StateGraph,START,END
from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage,BaseMessage
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages  
import streamlit as st
from langsmith import traceable
import os
#tool nodes
from src.tool import *
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from pathlib import Path

load_dotenv()

llm= ChatOpenAI()

#create state
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

#bind llm with tools
llm_with_tools=llm.bind_tools(tools)
#create a chatnode
def chat_node(state:State):
    messages=state['messages']
    response=llm_with_tools.invoke(messages)
    return {"messages":[response]}


#Memory 
PATH = Path(__file__).resolve().parent.parent
DATABASE=PATH / "database" / "chatbot.db"
conn = sqlite3.connect(DATABASE, check_same_thread=False)
checkpointer=SqliteSaver(conn=conn)

#create nodes and edges 
tool_node= ToolNode(tools) 
graph= StateGraph(State)
graph.add_node("Chat Node", chat_node)
graph.add_node("tools", tool_node)

#edge
graph.add_edge(START,"Chat Node")
graph.add_conditional_edges("Chat Node",tools_condition)
graph.add_edge("tools","Chat Node")


workflow=graph.compile(checkpointer=checkpointer)

#to extract number of threads
def retrieve_threads():
    all_threads=set()
    for checkpoints in checkpointer.list(None):
        all_threads.add(checkpoints.config["configurable"]["thread_id"])

    return list(all_threads)