from typing import List, Literal
from braintrust import init_logger, traced
from braintrust_langchain import BraintrustCallbackHandler, set_global_handler
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from pydantic import BaseModel
from langchain_core.output_parsers import PydanticOutputParser
from config import settings

handler = BraintrustCallbackHandler()
set_global_handler(handler)

# Create a ChatOpenAI model
model = ChatOpenAI(model="gpt-5.1-chat-latest", api_key=settings.OPENAI_API_KEY)

class ReviewedDescription(BaseModel):
    unclear_sections: List[str]
    jargon_terms: List[str]
    biased_language: List[str]
    missing_information: List[str]
    overall_summary: str

class RewrittenSection(BaseModel):
    category: Literal["clarity", "jargon", "bias", "missing_information"]
    original_text: str
    issue_explanation: str
    improved_text: str

class JDRewriteOutput(BaseModel):
    rewritten_sections: List[RewrittenSection]

class RevisedDescription(BaseModel):
    rewritten_description: str
    overall_summary: str


REVIEW_PROMPT = """
You are an expert HR job description analyst specializing in inclusive hiring practices.

Analyze the provided job description for potential issues across these dimensions:

1. CLARITY: Identify sections with vague responsibilities, unclear expectations, or ambiguous requirements.
   Flag phrases like "various duties," "other tasks as assigned," or undefined acronyms.

2. JARGON: Flag unnecessarily technical language inappropriate for the role level.
   Consider whether terms would be understood by qualified candidates unfamiliar with internal terminology.

3. BIAS: Identify language that may discourage diverse candidates:
   - Gender-coded words (e.g., "rockstar," "ninja," "aggressive," "nurturing")
   - Age bias (e.g., "digital native," "recent graduate")
   - Exclusionary phrases (e.g., "culture fit," "work hard/play hard")
   - Excessive requirements (unnecessarily requiring degrees or years of experience)

4. MISSING INFORMATION: Note absent critical details:
   - Salary range or compensation structure
   - Work location/arrangement (remote/hybrid/onsite)
   - Reporting structure or team context
   - Clear distinction between required vs. preferred qualifications
   - Application process and timeline
   - Growth/development opportunities

5. SUMMARY: Provide 2-3 sentences describing overall quality and primary concerns.

For each issue you identify:
- Quote the exact problematic text
- Explain why it is problematic

Your output MUST be valid JSON that conforms exactly to the provided schema.
Do not include any text outside the JSON.

If information is missing, return empty arrays.

Analyze the following job description:

--- JOB DESCRIPTION ---
{description}
----------------------

Return only JSON.

{format_instructions}
"""

REWRITE_SYSTEM_PROMPT = """
You are an expert HR editor specializing in rewriting job descriptions for clarity, inclusivity,
and accessibility.

You will receive:
1. The original job description.
2. A structured analysis of issues found in Step 1.

Your task is to rewrite ONLY the problematic sections, not the entire job description.

For each identified issue:
- Include the original problematic text (quoted exactly)
- Include the category (clarity, jargon, bias, or missing_information)
- Provide an improved, inclusive alternative that preserves meaning
- Maintain neutral, professional tone
- Ensure suggestions follow inclusive hiring practices

Return ONLY valid JSON matching the provided schema. Do not write any prose outside JSON.
"""

REWRITE_USER_PROMPT = """
Original Job Description:
-------------------------
{job_description}

Analysis Findings:
------------------
{analysis_json}

Rewrite ONLY the problematic sections using the schema.
Return only JSON.

{format_instructions}
"""

FINALISE_SYSTEM_PROMPT = """
You are an expert HR writer specializing in creating clear, concise, and inclusive job descriptions.

Your job is to produce the final polished version of the job description.

You will receive:
1. The original job description.
2. A list of rewritten sections (from Step 2).

Your tasks:
- Incorporate all improved rewritten sections into the original job description.
- Remove or replace the problematic text that was flagged in earlier steps.
- Maintain the original intent, structure, and role scope.
- Ensure clarity, inclusivity, and accessibility.
- Make tone consistent: professional, warm, and concise.
- Improve flow and readability where necessary.
- Do NOT invent new responsibilities, requirements, or benefits.

Return ONLY the final polished job description as plain text. Do not include JSON.
"""

FINALISE_USER_PROMPT = """
Original Job Description:
-------------------------
{job_description}

Rewritten Sections:
-------------------
{rewritten_sections_json}

Create the final polished job description by integrating the improvements.
Return only the final text.
"""

@traced(name="Review Job Description")
def review_description(description: str):
    
    review_parser = PydanticOutputParser(pydantic_object=ReviewedDescription)
    review_prompt = PromptTemplate(
      template=REVIEW_PROMPT,
        input_variables=["description"],
        partial_variables={"format_instructions": review_parser.get_format_instructions()},
      )
    review_chain = review_prompt | model | review_parser

    rewrite_parser = PydanticOutputParser(pydantic_object=JDRewriteOutput)
    rewrite_prompt = ChatPromptTemplate.from_messages([
        ("system", REWRITE_SYSTEM_PROMPT),
        ("human", REWRITE_USER_PROMPT),
    ]).partial(format_instructions=rewrite_parser.get_format_instructions())
    rewrite_chain = rewrite_prompt | model | rewrite_parser

    finalize_prompt = ChatPromptTemplate.from_messages([
        ("system", FINALISE_SYSTEM_PROMPT),
        ("human", FINALISE_USER_PROMPT),
    ])
    finalize_chain = finalize_prompt | model

    review_output: ReviewedDescription = review_chain.invoke({"description": description})
    rewrite_output: JDRewriteOutput = rewrite_chain.invoke({"job_description": description, "analysis_json": review_output.model_dump_json()})
    final_output = finalize_chain.invoke({"job_description": description, "rewritten_sections_json": rewrite_output.model_dump_json()})
    
    return RevisedDescription(rewritten_description=final_output.content, overall_summary=review_output.overall_summary)
    