from typing import List

from pydantic import BaseModel, Field
from config import settings
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser, PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5.1-chat-latest", api_key=settings.OPENAI_API_KEY)


# -------------------------
# Pydantic schema
# -------------------------
class Step(BaseModel):
    text: str = Field(description="ユーザーがそのまま実行できる1つの対応ステップ")
    kind: str = Field(default="action", description="action | check | caution など(UIでアイコン分けしたい時用)")

class Procedure(BaseModel):
    steps: List[Step] = Field(default_factory=list, description="上から順に実行する手順")


PROMPT_TEMPLATE = """
You are an assistant that creates a troubleshooting procedure from the provided context.

Rules:
- Use ONLY the provided context. Do NOT invent steps not supported by it.
- Output STRICTLY valid JSON only (no markdown, no extra text).
- Steps must be in a logical execution order.
- Each step must be a single, actionable instruction.
- If the context is insufficient, include clarifying questions in "questions".
- Use Japanese.

Context:
{context}

User issue:
{query}

{format_instructions}
"""

def docs_to_context(docs: List[Document]) -> str:
    parts: List[str] = []
    for i, d in enumerate(docs, start=1):
        parts.append(f"[EXCERPT {i}]\n{d.page_content}")
    return "\n\n---\n\n".join(parts)

def generate_procedure(query: str, vector_store):
    parser = PydanticOutputParser(pydantic_object=Procedure)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).partial(format_instructions=parser.get_format_instructions())
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    chain = (
        {
            "query": RunnablePassthrough(),
            "context": retriever | RunnableLambda(docs_to_context),
        }
        | prompt
        | model
        | parser
    )

    response = chain.invoke(query)
    return response
