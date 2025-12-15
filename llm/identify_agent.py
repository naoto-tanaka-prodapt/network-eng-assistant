from enum import Enum
from agents import Agent, set_default_openai_key, set_trace_processors
from braintrust import init_logger
from pydantic import BaseModel, Field
from typing import List
from config import settings

class MediaHint(str, Enum):
    physical = "physical"
    switch = "switch"
    network = "network"
    unknown = "unknown"

class IdentificationOutput(BaseModel):
    facts: str = Field(
        ...,
        description="List the facts that can be directly derived from the input (alarms / symptoms / errors / observations) in short sentences. Speculation is not allowed."
    )
    extracted_keywords: List[str] = Field(
        ...,
        description="Network technical keywords (e.g., device, port, protocol, test method). No duplicates."
    )
    media_hint: MediaHint = Field(
        ...,
        description="Indicates whether the issue is likely related to physical, network, or switch. Set to unknown if there is no evidence in the input."
    )

IDENTIFY_SYSTEM_PROMPT = """You are the Identify Agent of a network troubleshooting support system.

Objective:
Interpret user input (alarms / symptoms / error messages) and define what problem is occurring.
Your responsibility is limited to Identify (problem definition and keyword extraction).
Root cause analysis, remediation proposals, and test procedure suggestions are strictly prohibited.

Tasks:
- List the facts that can be read from the input (do not speculate).
- media_hint indicates whether the issue is likely related to physical / network / switch. If there is no evidence in the input, set it to unknown.
- extracted_keywords Extract keywords strictly limited to network-related technical terms, extracted based on the provided input. Maximum of 8 keywords.

Rules:
- Do not write anything that is not present in the input.
- Estimating causes, proposing countermeasures, presenting commands, or suggesting detailed test procedures are prohibited.
- The output must be JSON only and must conform to the specified schema.
"""

IDENTIFY_USER_PROMPT = """
Below are the alarms, symptoms, and error messages entered by the network engineer.:
{error_message}
"""

create_identify_agent = Agent(
    name="Identify_Agent",
    instructions=IDENTIFY_SYSTEM_PROMPT,
    model="gpt-4.1",
    output_type=IdentificationOutput
)
