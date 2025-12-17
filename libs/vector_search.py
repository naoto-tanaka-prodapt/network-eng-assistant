from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from config import settings
from qdrant_client.http import models as qm

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

def get_manual_documents(query: str, k: int, vector_store: QdrantVectorStore, part: str | None = None):
    search_kwargs = {"k": k}
    if part and part != "unknown":
        search_kwargs["filter"] = qm.Filter(
        must=[
            qm.FieldCondition(
                key="metadata.part",
                match=qm.MatchValue(value=part),
            )
        ]
    )

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs=search_kwargs
    )

    return retriever.invoke(query)


def format_context_from_docs(docs):
    blocks = []
    for d in docs:
        m = d.metadata or {}
        raw = d.page_content or ""
        blocks.append(
            "----\n"
            f"chunk_id: {m.get('chunk_id')}\n"
            f"part: {m.get('part')}\n"
            f"section_title: {m.get('section_title')}\n"
            f"page_start: {m.get('page_start')}  page_end: {m.get('page_end')}\n"
            f"text:\n{raw}\n"
        )
    return "\n".join(blocks)
