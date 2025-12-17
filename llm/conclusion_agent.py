from pydantic import BaseModel, Field
from agents import Agent, ModelSettings


class ConclusionOutput(BaseModel):
    title: str = Field(
        ...,
        description="Title that summarises the content in one sentence."
    )
    symptom: str = Field(
        ...,
        description="Symptoms/signs identifiable by the user or monitoring (e.g., error messages, reproduction conditions, behaviour)."
    )
    resolution: str = Field(
        ...,
        description="Solution (corrective action) written in natural language."
    )
    user_feedback: str = Field(
        ...,
        description="What the user can do if the same issue occurs again (actions, checks, information to report)."
    )
    guide: str = Field(
        ...,
        description="Guide content and page numbers referenced as evidence."
    )


CONCLUSION_SYSTEM_PROMPT = """You are the Doc & Feedback Agent for a network troubleshooting assistance system.

Objective:
Based on the results so far (Identification / Localization / Analysis / Action / Validation),
(1) Doc (reusable knowledge):
    Create a set of “identifiable symptom (signature) and resolution”.
    This will be the material for KB/Runbook that can be reused for similar future incidents.
(2) User feedback:
    Create actions, checks, and communications the user can perform if the same issue happens again.
    (e.g., record reproduction conditions, when/where/who, shown error messages, conditions that require immediate contact)

Constraints (IMPORTANT):
- Generate only from the session content.
- Do not add new diagnostics or fixes (only organise what is already determined/executed).
- Do not assert unobserved facts. If something is unknown, state “unknown” or use conditional wording.
- Write only content supported by the guide excerpts (do not mix in external rules).

Guidance for each field:
- title: generate a one-sentence title that summarises this case.
- symptom: include only information identifiable by the user/monitoring/simple checks.
  Examples: error messages, occurrence conditions, characteristics of the impact, reproducibility, time window, etc.
- resolution: concisely list the ordered steps that actually contributed to the fix.
  (Organise mainly around the fix_steps provided by Action.)
- user_feedback: limit to what the user can do next time (do not describe engineer tasks or configuration changes for the user).
    - Examples:
        - Tasks the user can perform
        - Conditions that require immediate escalation/contact
        - Information needed to speed up resolution next time
    - Avoid heavy jargon; short bullet-like wording is acceptable.

- guide: list the referenced guide excerpts with start_page / last_page / chapter.

Output requirements:
- Output must be JSON only.
- The JSON must contain exactly these five keys:
  1) symptom
  2) resolution
  3) user_feedback
  4) guide
  5) title
- Do not output extra keys, Markdown, preambles, or explanations.
"""

create_conclusion_agent = Agent(
    name="Conclusion_Agent",
    instructions=CONCLUSION_SYSTEM_PROMPT,
    model="gpt-4.1",
    model_settings=ModelSettings(
        temperature=0
    ),
    output_type=ConclusionOutput,
)
