import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

embeddings = OpenAIEmbeddings()

current_retriever = None

def build_retriever(file_path, chunk_size=500, chunk_overlap=200, k=2):
    """
    Creates a new retriever from a PDF file.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF not found at path: {file_path}")

    loader = PyPDFLoader(file_path)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, 
        chunk_overlap=chunk_overlap
    )
    chunks = splitter.split_documents(docs)

    vectordb = FAISS.from_documents(chunks, embeddings)

    retriever_obj = vectordb.as_retriever(
        search_type="similarity", 
        search_kwargs={"k": k}
    )
    
    return retriever_obj

def update_retriever(file_path):
    """
    Updates the global current_retriever with a new file.
    """
    global current_retriever
    try:
        current_retriever = build_retriever(file_path)
        print(f"RAG System updated with: {file_path}")
        return True
    except Exception as e:
        print(f"Failed to update RAG: {e}")
        return False

from pathlib import Path
PATH_DIR=Path(__file__).resolve().parent.parent
DATA_DIR= PATH_DIR / "data"

if os.path.exists(DATA_DIR):
    update_retriever(DATA_DIR)