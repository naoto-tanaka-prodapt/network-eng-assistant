from typing import Annotated
from agents import Runner, SQLiteSession
from fastapi import APIRouter, Depends, Form
from libs.db import get_session
from libs.vector_search import get_vector_store
from models import History
from schemas import IdentifyProblemForm, LocatingProblemForm, AnalyzeProblemForm, ActionProblemForm, ConclusionForm
from llm.identify_agent import create_identify_agent, IDENTIFY_USER_PROMPT, IdentificationOutput
from llm.locating_agent import LocatingOutput, create_locating_agent, LOCATING_USER_PROMPT
from llm.analyze_agent import create_analyze_agent, ANALYZE_USER_PROMPT
from llm.action_agent import create_action_agent, ACTION_USER_PROMPT
from llm.conclusion_agent import ConclusionOutput, create_conclusion_agent
from libs.vector_search import get_manual_documents, format_context_from_docs

router = APIRouter()

@router.post("/api/identify")
async def identify_problem(request: Annotated[IdentifyProblemForm, Form()]) -> IdentificationOutput:
    session = SQLiteSession(request.session_id, "conversations.db")
    user_input = IDENTIFY_USER_PROMPT.format(error_message=request.query)

    result = await Runner.run(create_identify_agent, user_input, session=session)

    return result.final_output

@router.post("/api/locating")
async def locating_problem(
    request: Annotated[LocatingProblemForm, Form()],
    vector_store=Depends(get_vector_store)
) -> LocatingOutput:
    session = SQLiteSession(request.session_id, "conversations.db")
    search_query = request.facts

    manuals = get_manual_documents(
        query=search_query,
        k=5,
        vector_store=vector_store,
        part=request.media_hint
    )

    manual_context = format_context_from_docs(manuals)

    user_input = LOCATING_USER_PROMPT.format(
        facts=request.facts,
        manual=manual_context
    )

    result = await Runner.run(
        create_locating_agent,
        user_input,
        session=session
    )

    return result.final_output

@router.post("/api/analyze")
async def analyze_problem(request: Annotated[AnalyzeProblemForm, Form()], vector_store=Depends(get_vector_store)):
    session = SQLiteSession(request.session_id, "conversations.db")
    manuals = get_manual_documents(
        query=request.locating_response,
        k=3,
        vector_store=vector_store,
        part=request.media_hint,
    )
    user_input = ANALYZE_USER_PROMPT.format(facts=request.facts , locating_response=request.locating_response, manual=format_context_from_docs(manuals))
    result = await Runner.run(create_analyze_agent, user_input, session=session)
    return result.final_output

@router.post("/api/action")
async def action_for_problem(request: Annotated[ActionProblemForm, Form()], vector_store=Depends(get_vector_store)):
    session = SQLiteSession(request.session_id, "conversations.db")
    manuals = get_manual_documents(
        query=request.root_cause,
        k=3,
        vector_store=vector_store,
        part=request.media_hint,
    )
    user_input = ACTION_USER_PROMPT.format(root_cause=request.root_cause, manual=format_context_from_docs(manuals))
    result = await Runner.run(create_action_agent, user_input, session=session)
    return result.final_output

@router.post("/api/conclusion")
async def conclusion(request: Annotated[ConclusionForm, Form()], db=Depends(get_session)):
    session = SQLiteSession(request.session_id, "conversations.db")
    result = await Runner.run(create_conclusion_agent, "", session=session)

    output: ConclusionOutput = result.final_output
    new_history = History(
        title = output.title,
        symptom = output.symptom,
        resolution = output.resolution,
        user_feedback = output.user_feedback,
        guide = output.guide
    )

    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    return new_history
