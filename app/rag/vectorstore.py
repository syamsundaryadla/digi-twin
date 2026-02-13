import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS

load_dotenv()

# Use Google's embedding API instead of local HuggingFace model
# This uses near-zero RAM (API call) vs ~400MB for torch + sentence-transformers
_embeddings = None

def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        api_key = os.getenv("GOOGLE_API_KEY", "").strip()
        print("[INFO] Initializing Google Embedding API...")
        _embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key
        )
        print("[SUCCESS] Google Embedding API ready.")
    return _embeddings

def create_vector_store(documents):
    embeddings = _get_embeddings()

    vectorstore = FAISS.from_documents(
        documents=documents,
        embedding=embeddings
    )

    return vectorstore
