import streamlit as st
import os
import shutil
from src.process import workflow, retrieve_threads
from src.rag import update_retriever 
from langchain_core.messages import HumanMessage, AIMessage
import uuid  

#Memory/Threads 
def generate_thread_id():
    return str(uuid.uuid4())  

def add_thread(thread_id):
    if "chat_thread" not in st.session_state:
         st.session_state["chat_thread"] = []
    if thread_id not in st.session_state["chat_thread"]:
        st.session_state["chat_thread"].append(thread_id)

def load_conversation(thread_id):
    state = workflow.get_state(config={"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])

def reset_chat():
    # Generate a new thread id and reset history
    new_thread_id = generate_thread_id()
    st.session_state["thread_id"] = new_thread_id
    add_thread(new_thread_id)
    st.session_state["message_history"] = []

#Initialize Session State
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_thread" not in st.session_state:
    st.session_state["chat_thread"] = retrieve_threads()

add_thread(st.session_state["thread_id"])



#Sidebar UI 
st.sidebar.title("LangGraph Chatbot")

#upload pdf here:
st.sidebar.header("Chat with a PDF")
uploaded_file = st.sidebar.file_uploader("Upload a PDF to chat with", type="pdf")

if uploaded_file is not None:
    if st.session_state.get("last_uploaded_file") != uploaded_file.name:
        
        #Ensure temp directory exists
        os.makedirs("temp_data", exist_ok=True)
        temp_path = os.path.join("temp_data", uploaded_file.name)
        
        # Save the file to disk
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Update the RAG system
        with st.sidebar.status("Processing PDF..."):
            success = update_retriever(temp_path)
            if success:
                st.sidebar.success("PDF Processed & Ready!")
                st.session_state["last_uploaded_file"] = uploaded_file.name
            else:
                st.sidebar.error("Failed to process PDF")
st.sidebar.markdown("---")

if st.sidebar.button("New Chat"):
    reset_chat()

st.sidebar.header("My Conversations")

#Display all conversation threads
if st.session_state["chat_thread"]:
    #Reverse list to show newest first
    for thread_id in st.session_state["chat_thread"][::-1]:
        # usage of key=thread_id ensures each button is unique
        if st.sidebar.button(str(thread_id), key=thread_id):
            st.session_state["thread_id"] = thread_id
            messages = load_conversation(thread_id)
            
            # Reconstruct history for UI
            temp_messages = []
            for message in messages:
                if isinstance(message, HumanMessage):
                    temp_messages.append({"role": "user", "content": message.content})
                # Only show AI messages that have text (skipping internal tool calls)
                elif isinstance(message, AIMessage) and message.content:
                    temp_messages.append({"role": "assistant", "content": message.content})
            
            st.session_state["message_history"] = temp_messages
            st.rerun()



#Chat Display
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])




#Chat Input 
user_input = st.chat_input("Type something here")

if user_input:
    #Add user message
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Config for LangGraph
    config = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "run_name": "chat_turn"
    }

    # Generate assistant reply
    with st.chat_message("assistant"):
        def ai_only_messages():
            for message_chunk, metadata in workflow.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=config,
                stream_mode="messages",
            ):
                if isinstance(message_chunk, AIMessage) and message_chunk.content:
                    yield message_chunk.content
        
        ai_message_content = st.write_stream(ai_only_messages)

    if ai_message_content:
        st.session_state["message_history"].append(
            {"role": "assistant", "content": ai_message_content}
        )