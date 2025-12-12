# from functools import lru_cache
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from config import settings
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from langchain_core.documents import Document

COLLECTION_NAME = "frontline_lan_metadata"

def get_vector_store():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=settings.OPENAI_API_KEY)
    if settings.PRODUCTION:
        vector_store = QdrantVectorStore.from_existing_collection(
            embedding=embeddings, 
            collection_name=COLLECTION_NAME, 
            url=str(settings.QDRANT_URL), 
            api_key=settings.QDRANT_API_KEY
        )
    else:
        vector_store = QdrantVectorStore.from_existing_collection(embedding=embeddings, collection_name=COLLECTION_NAME, path="qdrant_store")
    return vector_store

# def inmemory_vector_store():
#     embeddings = OpenAIEmbeddings(model="text-embedding-3-large", api_key=settings.OPENAI_API_KEY)
#     client = QdrantClient(":memory:")
#     client.create_collection(collection_name="resumes", vectors_config=VectorParams(size=3072, distance=Distance.COSINE))
#     vector_store = QdrantVectorStore(client=client, collection_name="resumes", embedding=embeddings)
    
#     try:
#         yield vector_store
#     finally:
#         client.close()

def get_manual_documents(query: str, vector_store: QdrantVectorStore):
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    manuals = retriever.invoke(query)
    return manuals
