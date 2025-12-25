# AgentGraph AI 🤖

An Agentic AI Chatbot built with LangGraph, Streamlit, and OpenAI.
Supports multi-threaded conversations, tool-augmented reasoning, RAG-based document search,
and persistent memory using SQLite.


## Features


### Interactive Streamlit chat interface

### Integrated with LangGraph for structured workflows

### SQLite-based memory for chat history and threads


## Custom tools:

Calculator Tool (add, sub, mul, div)
Stock Price Tool (using Alpha Vantage API)
Tavily Search Tool (for web search)
RAG for external search



## Clone the repository
```bash
git clone <your-repo-link>
cd project
```

## Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate   #for windows    
```

## Install dependencies
```bash
pip install -r requirements.txt
```

## Add your environment variables

OPENAI_API_KEY=your_openai_api_key
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key
TAVILY_API_KEY=your_tavily_key
LANGCHAIN_API_KEY=langchain_api_key
LANGCHAIN_PROJECT='Langgraph Chatbot'

## Run the App
Run locally
```bash
streamlit run app.py
```

## run with Docker
```bash
docker build -t langgraph-chatbot .
docker run -p 8501:8501 --env-file Agentic_Chatbot/.env langgraph-chatbot
```