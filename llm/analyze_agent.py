from typing import List
from pydantic import BaseModel, Field
from agents import Agent, ModelSettings
from llm.agent_common_model import GuideBasisItem


class AnalysisOutput(BaseModel):
    """
    Step: Analysing the problem — determining root cause from measurements and system behaviour
    """
    root_cause: str = Field(
        ...,
        description="Smallest single cause that most reasonably explains the observed results."
    )
    reasoning: str = Field(
        ...,
        description="Short explanation of observation (measurement/behaviour) → interpretation → conclusion."
    )
    guide_basis: List[GuideBasisItem] = Field(
        ...,
        description="Guide chunks referenced as evidence for this output (at least one)."
    )


ANALYZE_SYSTEM_PROMPT = """You are the Analyse Agent for a network troubleshooting assistance system.

Objective:
For the test items suggested by the Location Agent, a network engineer inputs what was performed/observed (measurements, logs, behaviour) in natural language.
Interpret those observations and, based on the measurements and system behaviour, identify the root cause.

Constraints (IMPORTANT):
- Do not propose fix steps, configuration changes, mitigations, or next tests (handled by Action/Localization).
- Do not assert facts that were not observed. If assumptions are needed, mark them explicitly as “assumption” in reasoning.
- Prioritise interpretations supported by the guide excerpts; do not mix in outside knowledge.
- Narrow the root cause down to a single cause whenever possible. If you truly cannot narrow it,
  briefly note uncertainty in reasoning and what additional observations are needed (what is missing),
  but do not write procedures for additional observations—only explain what is lacking.

Output requirements:
- Output must be JSON only.
- The JSON must include exactly these three keys:
  1) root_cause: root cause based on the observations (concise)
  2) reasoning: brief explanation of observation (measurement/behaviour) → interpretation → conclusion (no asserting unobserved facts)
  3) guide_basis: list of guide excerpts used as evidence (at least one)
     - Each item must include start_page / last_page / chapter / note
     - start_page/last_page/chapter must reuse the metadata provided with the input guide excerpts
     - In note, briefly state which observation/interpretation it supports

Additional rules:
- Never output extra keys.
- Do not output Markdown, explanations, or preambles (JSON only).
"""

ANALYZE_USER_PROMPT = """
Here is the original task:

{manual}

Here is what the network engineer confirmed for the test items:

{locating_response}


Here are the retrieved manual excerpts:

{manual}
"""

create_analyze_agent = Agent(
    name="Analyze_Agent",
    instructions=ANALYZE_SYSTEM_PROMPT,
    model="gpt-4.1",
    model_settings=ModelSettings(
        temperature=0
    ),
    output_type=AnalysisOutput,
)
