from typing import List, Literal, Optional

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
PhaseName = Literal["identification", "localization", "analysis", "action", "verification"]

class Citation(BaseModel):
    chunk_id: str = Field(..., description="Retrieved chunk_id (unique).")
    page_start: int = Field(..., description="0-based page index start.")
    page_end: int = Field(..., description="0-based page index end.")
    section_path: List[str] = Field(default_factory=list, description="TOC-based section path/title.")
    part: Optional[str] = Field(None, description="intro|physical|network|switches|... if available")

class Step(BaseModel):
    title: str = Field(..., description="Short step title (<= 12 words).")
    instruction: str = Field(..., description="What to do, based ONLY on retrieved manual text.")
    expected_result: Optional[str] = Field(None, description="What you expect to observe after the step (if stated in manual).")
    citations: List[Citation] = Field(..., description="One or more citations supporting this step.")

class PhaseOutput(BaseModel):
    phase: PhaseName
    steps: List[Step] = Field(default_factory=list, description="Steps for this phase. Can be empty if not found.")

class SafetyCheck(BaseModel):
    warning: str = Field(..., description="Safety / risk / caution statement grounded in the manual.")
    risk: Literal["low", "medium", "high", "unknown"] = "unknown"
    citations: List[Citation] = Field(...)

class TroubleshootingResponse(BaseModel):
    issue_summary: str = Field(..., description="One-sentence summary of the user's issue.")
    assumptions: List[str] = Field(default_factory=list, description="Assumptions made due to missing info, if any.")
    phases: List[PhaseOutput] = Field(..., description="Exactly 5 phases in order.")
    safety_checks: List[SafetyCheck] = Field(default_factory=list)
    not_found: List[str] = Field(default_factory=list, description="What could not be found in the manual/retrieved context.")



PROMPT_TEMPLATE = """You are a frontline LAN troubleshooting assistant.
You MUST follow the provided manual excerpts (context). Do NOT invent steps or facts.
Every step and every safety check MUST have at least one citation from the provided context.
If the manual does not contain an answer in the provided context, say so in `not_found` and leave the phase steps empty.

You must structure your answer into 5 phases:
1) identification
2) localization
3) analysis
4) action
5) verification

Safety checks are cross-cutting and must be listed separately when present in the context.

Context:
{context}

User issue:
{query}

{format_instructions}
"""

def format_context_from_docs(docs):
    blocks = []
    for d in docs:
        m = d.metadata or {}
        raw = d.page_content or ""
        blocks.append(
            "----\n"
            f"chunk_id: {m.get('chunk_id')}\n"
            f"part: {m.get('part')}\n"
            f"section_path: {m.get('section_path')}\n"
            f"page_start: {m.get('page_start')}  page_end: {m.get('page_end')}\n"
            f"text:\n{raw}\n"
        )
    return "\n".join(blocks)


def generate_procedure(query: str, vector_store):
    parser = PydanticOutputParser(pydantic_object=TroubleshootingResponse)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE).partial(format_instructions=parser.get_format_instructions())
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})

    chain = (
        {
            "query": RunnablePassthrough(),
            "context": retriever | RunnableLambda(format_context_from_docs),
        }
        | prompt
        | model
        | parser
    )

    response = chain.invoke(query)
    return response
