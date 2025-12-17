"""
Run the agent chain for predefined inputs and export results to CSV.
Analyze input is auto-generated from the locating outputs using OpenAI.
"""

import asyncio
import csv
import json
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from openai import OpenAI

from agents import Runner, SQLiteSession, set_default_openai_key
from config import settings
from libs.vector_search import format_context_from_docs, get_manual_documents, get_vector_store
from llm.action_agent import ACTION_USER_PROMPT, create_action_agent
from llm.analyze_agent import ANALYZE_USER_PROMPT, create_analyze_agent
from llm.identify_agent import IDENTIFY_USER_PROMPT, create_identify_agent, MediaHint
from llm.locating_agent import LOCATING_USER_PROMPT, create_locating_agent


@dataclass
class CaseInput:
    testcase: str
    query: str


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
CASES: List[CaseInput] = [
    CaseInput(
        testcase="P1",
        query="The link does not come up at a newly installed workstation. The wiremap test fails.",
    ),
    CaseInput(
        testcase="P2",
        query="A Cat6A cabling link fails certification testing. The link occasionally goes down.",
    ),
    CaseInput(
        testcase="P3",
        query="The network becomes slow only at specific times of the day.",
    ),
    CaseInput(
        testcase="F1",
        query="The optical link does not come up.",
    ),
    CaseInput(
        testcase="N1",
        query="Cannot connect to the server from this PC.",
    ),
    CaseInput(
        testcase="N2",
        query="The network connection drops after it has been up for a while.",
    ),
    CaseInput(
        testcase="N3",
        query="This PC is much slower than other PCs on the same network.",
    ),
    CaseInput(
        testcase="S1",
        query="Users connected to this switch are experiencing high latency.",
    ),
]

OUTPUT_PATH = Path("agents_output.csv")


def _to_json(value: object) -> str:
    """Serialize agent output to a JSON string (empty string when None)."""
    if value is None:
        return ""
    try:
        # pydantic models expose model_dump; fall back to raw object otherwise
        if hasattr(value, "model_dump"):
            value = value.model_dump()  # type: ignore
        return json.dumps(value, ensure_ascii=False, indent=2)
    except Exception:
        return str(value)


def _build_analyze_input(client: OpenAI, identify_output, locating_output, locate_manual: str) -> str:
    prompt = f"""You are preparing input for the Analyze agent.

This is NOT a summary task.

Your task:
- Restate ONLY the observations that were explicitly confirmed during the locating phase.
- Treat the locating output as a record of user-confirmed checks and test results.
- Do NOT interpret, summarize, generalize, or prioritize.
- Do NOT infer causes, suggest fixes, or add missing observations.
- If something was not explicitly confirmed in the locating output, do NOT include it.

Inputs:

[Identify summary]
{identify_output}

[Locating output (confirmed checks and results)]
{_to_json(locating_output)}

[Manual excerpts referenced during locating]
{locate_manual}

Output rules:
- Use bullet points only.
- Each bullet must correspond to a concrete, confirmed observation
  (e.g., a test result, a yes/no confirmation, a measured value).
- Preserve uncertainty (e.g., "not confirmed", "unknown") if present.
- Avoid any interpretive language ("suggests", "likely", "indicates", "implies").

Return ONLY the list of confirmed observations.
"""
    resp = client.responses.create(
        model="gpt-5.1",
        input=[{"role": "user", "content": prompt}],
    )
    return resp.output_text.strip()




async def run_case(case: CaseInput, vector_store) -> Dict[str, str]:
    session = SQLiteSession(f"{case.testcase}-{uuid.uuid4()}")
    record: Dict[str, str] = {
        "testcase": case.testcase,
        "input": case.query,
        "identify": "",
        "locating_manual": "",
        "locating": "",
        "analyze input": "",
        "analyze_manual": "",
        "analyze": "",
        "action_manual": "",
        "Action": "",
        "validate": "",
        "error": "",
    }

    try:
        identify_prompt = IDENTIFY_USER_PROMPT.format(error_message=case.query)
        identify_result = await Runner.run(create_identify_agent, identify_prompt, session=session)
        identify_output = identify_result.final_output
        record["identify"] = _to_json(identify_output)

        media_hint = getattr(identify_output, "media_hint", MediaHint.unknown)
        media_hint_value = media_hint.value if hasattr(media_hint, "value") else str(media_hint)
        locating_docs = get_manual_documents(
            query=identify_output.facts,
            k=5,
            vector_store=vector_store,
            part=media_hint_value,
        )
        locating_manual = format_context_from_docs(locating_docs)
        record["locating_manual"] = locating_manual

        locating_prompt = LOCATING_USER_PROMPT.format(facts=identify_output.facts, manual=locating_manual)
        locating_result = await Runner.run(create_locating_agent, locating_prompt, session=session)
        record["locating"] = _to_json(locating_result.final_output)

        # Build analyze input from locating output using OpenAI
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        analyze_input = _build_analyze_input(client, identify_output, locating_result.final_output, locating_manual)
        record["analyze input"] = analyze_input

        analyze_docs = get_manual_documents(
            query=analyze_input,
            k=3,
            vector_store=vector_store,
            part=media_hint_value,
        )
        analyze_manual = format_context_from_docs(analyze_docs)
        record["analyze_manual"] = analyze_manual

        analyze_prompt = ANALYZE_USER_PROMPT.format(
            facts=identify_output.facts,
            locating_response=analyze_input,
            manual=analyze_manual,
        )
        analyze_result = await Runner.run(create_analyze_agent, analyze_prompt, session=session)
        analyze_output = analyze_result.final_output
        record["analyze"] = _to_json(analyze_output)

        action_docs = get_manual_documents(
            query=analyze_output.root_cause,
            k=3,
            vector_store=vector_store,
            part=media_hint_value,
        )
        action_manual = format_context_from_docs(action_docs)
        record["action_manual"] = action_manual

        action_prompt = ACTION_USER_PROMPT.format(root_cause=analyze_output.root_cause, manual=action_manual)
        action_result = await Runner.run(create_action_agent, action_prompt, session=session)
        record["Action"] = _to_json(action_result.final_output)
    except Exception as exc:  # noqa: BLE001
        record["error"] = str(exc)

    return record


async def main() -> None:
    set_default_openai_key(settings.OPENAI_API_KEY)
    vector_store = get_vector_store()

    rows: List[Dict[str, str]] = []
    for case in CASES:
        print(f"[+] Running agents for {case.testcase} ...")
        rows.append(await run_case(case, vector_store))

    output_path = OUTPUT_PATH.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "testcase",
        "input",
        "identify",
        "locating_manual",
        "locating",
        "analyze input",
        "analyze_manual",
        "analyze",
        "action_manual",
        "Action",
        "validate",
        "error",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[✓] Wrote {len(rows)} rows to {output_path}")


if __name__ == "__main__":
    asyncio.run(main())
