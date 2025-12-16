from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field
from agents import Agent


class GuideBasisItem(BaseModel):
    start_page: str = Field(..., description="Starting page of the referenced guide chunk")
    last_page: str = Field(..., description="Ending page of the referenced guide chunk")
    chapter: str = Field(..., description="Chapter or section title of the referenced guide chunk")
    note: Optional[str] = Field(
        default=None,
        description="What this reference is used for (e.g., 'safety check', 'test procedure', 'decision criteria')"
    )


class SafetyCheckItem(BaseModel):
    content: str = Field(
        ...,
        description="Mandatory safety check to perform before or during diagnostics"
    )
    guide_basis: GuideBasisItem = Field(
        ...,
        description="Guide chunk used as the basis for this safety check"
    )


class LocatingItem(BaseModel):
    test_content: str = Field(..., description="切り分けのための確認項目（マニュアルに基づく）")
    purpose: str = Field(
        ...,
        description="この確認で何を切り分けたいか"
    )
    success_criteria: str = Field(
        ...,
        description="Observable condition under which this step is considered successful"
    )
    fail_criteria: str = Field(
        ...,
        description="Observable condition under which this step is considered failed"
    )
    next_step_rule: str = Field(
        ...,
        description="Rule describing what the next diagnostic step is based on success or failure (Location only)"
    )
    ask_back: str = Field(
        ...,
        description="ユーザが次に返すべき観測/結果"
    )
    # 各項目を“どこから引いたか”を必須にする
    guide_basis: GuideBasisItem = Field(
        ...,
        description="この項目の根拠として参照したガイドchunk"
    )


class LocatingOutput(BaseModel):
    """
    Step: Locating — using tests to isolate the fault and narrow impacted components.
    """
    safety_checks: List[SafetyCheckItem] = Field(
        ...,
        description="必須安全チェック。漏れ防止のため必ず出す。"
    )
    test_in_order: List[LocatingItem] = Field(
        ...,
        description="test、確認項目。"
    )


# ---- Prompts ----
LOCATING_SYSTEM_PROMPT = """You are the Locating Agent for a network troubleshooting assistance system.

Objective:
Using the Identify results (facts / keywords / media_hint) and the retrieved manual excerpts,
produce a logically ordered diagnostic plan (Location phase) that uses tests to isolate the fault and narrow down the impacted components.

Core principle (MUST follow):
- Execute diagnostic tests in a logical sequence as described in the manual.
- Verify the outcome of each step BEFORE moving to the next step.
- Apply preventive precautions to protect system stability and safety.

Constraints (IMPORTANT):
- Do NOT infer or conclude the root cause.
- Do NOT propose corrective actions or configuration changes.
- Do NOT provide repair or remediation steps.
- Stay strictly within the Location phase.

Manual usage (CRITICAL):
- Use ONLY content explicitly supported by the provided manual excerpts.
- Do NOT include any test, method, or decision rule that is not supported by the manual.
- Every safety check and diagnostic step MUST include a guide_basis reference
  (start_page, last_page, chapter).
- In guide_basis.note, briefly state how the manual excerpt is used
  (e.g., "safety check", "test procedure", "decision criteria", "prerequisite").

Reference integrity (NO GUESSING):
- Use page/chapter values ONLY if they are explicitly present in manual.
- If page or chapter information is not present, set the value to "unknown".
- Never invent references.

Required structure for EACH diagnostic step (LocatingItem):
For every item in test_in_order, you MUST provide:
- test_content: a concrete diagnostic or verification step from the manual
- purpose: what this step is intended to isolate or verify
- success_criteria: an observable PASS condition described or implied by the manual
- fail_criteria: an observable FAIL condition described or implied by the manual
- next_step_rule: what diagnostic step to perform next for SUCCESS vs FAILURE
  (must remain within the Location phase)
- ask_back: exactly what observation or result the user must report

General rule for test follow-up (IMPORTANT):
- Any diagnostic test mentioned in the manual that can PASS or FAIL
  MUST include explicit success_criteria, fail_criteria, and next_step_rule.
- If a test FAILS, the next_step_rule MUST describe further isolation
  (e.g., narrowing to cable, port, adapter, or local segment),
  not repair or configuration changes.
- If a test PASSES, the next_step_rule MUST describe the next isolation step
  or scope check supported by the manual.

Scope isolation:
- If the manual supports determining whether the issue affects
  a single station, a small group, or a broader area,
  include at least one step that performs this scope isolation.

Output requirements (MANDATORY):
Return JSON ONLY (must conform to the Pydantic schema) with exactly these fields:
1) safety_checks: an array of mandatory safety check items
2) test_in_order: an array of LocatingItem steps in logical order

Output rules:
- Output JSON only.
- Do NOT include extra keys, Markdown, explanations, or prefaces.

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
    model="gpt-5.2",
    output_type=LocatingOutput,
)
