import os
from dotenv import load_dotenv

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda


load_dotenv()  


def build_rag_chain(vectorstore):
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash",
        temperature=0.3,
        api_key=os.getenv("GOOGLE_API_KEY")  # 👈 explicit key
    )

    prompt = ChatPromptTemplate.from_template(
        """
        You are a personalized AI assistant. You are talking to {user_name}.

        Use the following user memory to answer the question.

        User Memory:
        {context}

        Question:
        {question}

        Answer in simple and clear English.
        """
    )

    def retrieve_context(question, user_id):
        # Perform similarity search with metadata filtering
        # We want docs that match user_id OR are global (user_id=-1)
        # FAISS doesn't support "OR" logic in simple filter dict usually.
        # We might need to fetch separately or use a custom filter function if supported.
        # LangChain FAISS `filter` argument usually maps to exact match on metadata fields.
        
        # Simple approach: Fetch for user specifically.
        # Problem: Losing global context (file).
        # Workaround: Retrieve top K for user AND top K for global, then combine.
        
        try:
            # 1. User Specific (Dynamic Memories)
            # The filter format depends on the vectorstore implementation.
            # Only apply filter if user_id is provided and valid
            docs_user = []
            if user_id: 
                 # Convert integer if needed, but metadata saved it as it was (int).
                 # FAISS in LangChain typically supports basic dict filtering.
                 docs_user = vectorstore.similarity_search(question, k=3, filter={"user_id": int(user_id)})
            
            # 2. Global (System Memories / Story)
            docs_global = vectorstore.similarity_search(question, k=2, filter={"user_id": -1})
            
            # Combine and Deduplicate
            all_docs = docs_user + docs_global
            return "\n".join(doc.page_content for doc in all_docs)
            
        except Exception as e:
            print(f"Retrieval Error: {e}")
            return ""

    rag_chain = (
        {
            "context": RunnableLambda(lambda x: retrieve_context(x["question"], x.get("user_id"))),
            "question": RunnableLambda(lambda x: x["question"]),
            "user_name": RunnableLambda(lambda x: x["user_name"])
        }
        | prompt
        | llm
    )

    return rag_chain
