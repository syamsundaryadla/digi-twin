from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Singleton: Load embedding model once, reuse on every RAG rebuild
_embeddings = None

def _get_embeddings():
    global _embeddings
    if _embeddings is None:
        print("[INFO] Loading embedding model (one-time)...")
        _embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        print("[SUCCESS] Embedding model loaded.")
    return _embeddings

def create_vector_store(documents):
    embeddings = _get_embeddings()

    vectorstore = FAISS.from_documents(
        documents=documents,
        embedding=embeddings
    )

    return vectorstore
