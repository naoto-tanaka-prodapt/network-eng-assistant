from typing import List
from config import settings
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5.1-chat-latest", api_key=settings.OPENAI_API_KEY)

prompt_template = """
You are an intelligent assistant tasked with answering user queries based on provided context. 
Use the following context to respond to the user's question.

Context:
{context}

Question:
{query}

Answer:
"""

def _docs_to_context(docs: List[Document]) -> str:
    chunks = []
    for d in docs:
        src = d.metadata.get("source") if hasattr(d, "metadata") else None
        if src:
            chunks.append(f"[source: {src}]\n{d.page_content}")
        else:
            chunks.append(d.page_content)
    return "\n\n---\n\n".join(chunks)

def generate_procedure(query: str, vector_store):
    prompt = ChatPromptTemplate.from_template(prompt_template)
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    chain = (
        {
            "query": RunnablePassthrough(),
            "context": retriever | RunnableLambda(_docs_to_context),
        }
        | prompt
        | model
        | StrOutputParser()
    )

    response = chain.invoke(query)
    return response
