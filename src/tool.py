from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.tools import tool
import requests
import src.rag as rag_system 

search_tool = TavilySearchResults()


@tool
def calculator(n1: float, n2: float, operation: str) -> dict:
    """
    Perform mathematical operations on two numbers.
    Supported operations: add, sub, mul, div
    """
    try:
        if operation == "add":
            result = n1 + n2
        elif operation == "sub":
            result = n1 - n2
        elif operation == "mul":
            result = n1 * n2
        elif operation == "div":
            if n2 == 0:
                return {"error": "division by zero not allowed"}
            result = n1 / n2
        else:
            return {"error": f'unsupported operation "{operation}"'}

        return {"n1": n1, "n2": n2, "operation": operation, "result": result}
    except Exception as e:
        return {"error": str(e)}

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch the latest stock price for the given symbol (e.g., 'AAPL', 'TSLA')
    using the Alpha Vantage API.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=6OEI5ZVB2RS2AECF"
    try:
        r = requests.get(url)   
        return r.json()
    except Exception as e:
        return {"error": "Failed to fetch stock data"}

@tool
def rag_tool(query: str):
    """
    Retrieve relevant information from the uploaded pdf document.
    Use this tool when the user ask factual/conceptual question that might be 
    answered from the stored documents.
    """
    if rag_system.current_retriever is None:
        return {"error": "No PDF document has been uploaded or processed yet."}
        
    result = rag_system.current_retriever.invoke(query)
    context = [doc.page_content for doc in result]
    metadata = [doc.metadata for doc in result]

    return {
        'query': query,
        'context': context,
        'metadata': metadata
    }

tools = [get_stock_price, calculator, search_tool, rag_tool]