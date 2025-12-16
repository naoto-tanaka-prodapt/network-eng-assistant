from typing import List
from pydantic import BaseModel, Field
from agents import Agent
from llm.agent_common_model import GuideBasisItem


class ActionOutput(BaseModel):
    """
    Step: Taking corrective action — applying fixes and verifying their effectiveness.
    Note: In this task, safety/stability/rollback are mandatory.
    """
    fix_steps: List[str] = Field(
        ...,
        description="Ordered corrective actions to perform. Keep concise if configuration changes or work instructions are included."
    )

    safety_checks: List[str] = Field(
        ...,
        description="Safety checks that must be performed before and during work (mandatory)."
    )

    impact_assessment: str = Field(
        ...,
        description="Assessment of impact scope, severity, and timing (mandatory)."
    )

    rollback_plan: List[str] = Field(
        ...,
        description="Steps to restore the system if the action fails (mandatory)."
    )

    guide_basis: List[GuideBasisItem] = Field(
        ...,
        description="Guide chunks referenced as evidence for this output (at least one)."
    )



ACTION_SYSTEM_PROMPT = """
You are the Action Agent for a network troubleshooting assistance system.

Objective:
Use the root cause identified by the Analyze Agent, along with its evidence (measurements/behaviour), to propose corrective actions.
Because this system is a “retrieval assistant”, only present content grounded in the provided guide excerpts.

Constraints (IMPORTANT):
- Do not propose corrective actions that lack support in the guide excerpts.
- Do not re-estimate the cause (handled by the Analysis phase).
- Follow logical order (preparation → execution → minimal verification if necessary).
- Prioritise system stability and safety (always include safety checks, impact assessment, and rollback).

Output requirements (MANDATORY):
The output JSON must include all five items below; none may be empty.
1) fix_steps: ordered corrective action steps
2) safety_checks: safety checks before/during work (required)
3) impact_assessment: impact assessment (required)
4) rollback_plan: steps to restore the system if the action fails (required)
5) guide_basis: list of guide excerpts used as evidence (at least one)

How to provide evidence:
- guide_basis must include start_page / last_page / chapter for the referenced guide excerpt.
- In note, briefly state which output (safety check/step/rollback, etc.) the citation supports.

Forbidden:
- Do not output extra keys.
- Do not output Markdown, explanations, or preambles (JSON only).
"""

ACTION_USER_PROMPT = """
Below is the cause identified by the Analyze Agent:

{root_cause}


Below are the retrieved manual excerpts:

{manual}
"""

create_action_agent = Agent(
    name="Action_Agent",
    instructions=ACTION_SYSTEM_PROMPT,
    model="gpt-4.1",
    output_type=ActionOutput,
)
