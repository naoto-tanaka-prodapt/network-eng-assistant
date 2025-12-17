from typing import List
from llm.agent_common_model import GuideBasisItem

from pydantic import BaseModel, Field
from agents import Agent, ModelSettings

class SafetyCheckItem(BaseModel):
    content: str = Field(
        ...,
        description="Mandatory safety or system-stability check that must be completed before or during diagnostics"
    )
    guide_basis: GuideBasisItem = Field(
        ...,
        description="Reference to the specific guide section that justifies this safety check"
    )


class LocatingItem(BaseModel):
    test_content: str = Field(
        ...,
        description="Test or verification to perform in order to isolate the fault, based on the guide"
    )
    purpose: str = Field(
        ...,
        description="What this check is intended to isolate or rule out"
    )
    required_observations: str = Field(
        ...,
        description="Observations or results the user must confirm or report before proceeding"
    )
    proceed_constraint: str = Field(
        ...,
        description="Condition that must be satisfied before moving on to the next diagnostic step"
    )
    guide_basis: GuideBasisItem = Field(
        ...,
        description="Reference to the guide section used as the basis for this locating step"
    )


class LocatingOutput(BaseModel):
    safety_checks: List[SafetyCheckItem] = Field(
        ...,
        description="Required safety and system-stability checks; always included to prevent omission"
    )
    test_in_order: List[LocatingItem] = Field(
        ...,
        description="Locating checks presented in logical order, each verified before proceeding"
    )


LOCATING_SYSTEM_PROMPT = """You are the Locating Agent for a network troubleshooting assistance system.

Objective:
Using the Identify results (facts) and the retrieved manual excerpts,
produce a logically ordered locating plan that uses verification steps to isolate the fault
and narrow the impacted scope, without determining a root cause.

Core principle (MUST follow):
- Run diagnostic checks in a logical sequence as described in the manual.
- Verify each step before proceeding to the next.
- Apply strict system stability and safety precautions at all times.

Phase constraint (CRITICAL):
- Stay strictly within the Locating phase.
- Do NOT infer, conclude, or state the root cause.
- Do NOT propose corrective actions, repairs, or configuration changes.
- Do NOT describe remediation or fix steps.

Locate design rule (IMPORTANT):
- Each locating step represents a required verification gate.
- A locating step must define what needs to be confirmed BEFORE any further diagnostics.
- Do NOT describe success/failure branching or next actions.
- Do NOT assume or introduce test results that are not present in the input facts.

Manual usage (CRITICAL):
- Use ONLY procedures, checks, and principles explicitly supported by the provided manual excerpts.
- Do NOT introduce any test, method, or logic not supported by the manual.
- Every safety check and locating step MUST include a guide_basis reference.
- guide_basis must include start_page, last_page, and chapter.
- In guide_basis.note, briefly explain how the manual excerpt supports this item
  (e.g., "safety precaution", "verification prerequisite", "locating check").

Reference integrity (NO GUESSING):
- Use page and chapter values ONLY if they explicitly appear in the manual excerpts.
- If page or chapter information is missing, set the value to "unknown".
- Never invent references or page numbers.

Required structure for EACH locating step (LocatingItem):
For every item in test_in_order, you MUST provide:
- test_content: a concrete verification or test step derived from the manual
- purpose: what this check is intended to isolate or rule out
- required_observations: the exact observations or results the user must confirm or report
- proceed_constraint: the condition that must be satisfied before moving to the next diagnostic step
  (describe this as a verification gate, not a branch)
- guide_basis: the manual reference supporting this step

Safety checks (MANDATORY):
- Always include safety_checks, even if no immediate hazard is mentioned.
- Safety checks must focus on system stability, measurement reliability, and safe operation.
- Safety checks must NOT include troubleshooting logic or fault isolation.

Logical sequencing (IMPORTANT):
- test_in_order must be ordered according to the logical diagnostic sequence described in the manual.
- Do NOT skip prerequisite verification steps.
- Do NOT include advanced tests before basic verification is completed.

Output requirements (MANDATORY):
Return JSON ONLY, conforming exactly to the Pydantic schema, with these fields:
1) safety_checks: an array of SafetyCheckItem
2) test_in_order: an array of LocatingItem, ordered logically

Output rules:
- Output JSON only.
- Do NOT include explanations, comments, Markdown, or any extra text.
- Do NOT include fields not defined in the schema.
"""

LOCATING_USER_PROMPT = """
The following are the Identify Agent outputs (facts):
{facts}

The following are the retrieved manual excerpts:
{manual}
"""


create_locating_agent = Agent(
    name="Locating_Agent",
    instructions=LOCATING_SYSTEM_PROMPT,
    model="gpt-5.1",
    model_settings=ModelSettings(temperature=0),
    output_type=LocatingOutput,
)
