from typing import Annotated
from agents import Runner, SQLiteSession
from fastapi import APIRouter, Depends, Form
from libs.vector_search import get_vector_store
from schemas import IdentifyProblemForm, LocatingProblemForm, AnalyzeProblemForm, ActionProblemForm, ValidateActionForm, ConclusionForm
from llm.identify_agent import create_identify_agent, IDENTIFY_USER_PROMPT
from llm.locating_agent import create_locating_agent, LOCATING_USER_PROMPT
from llm.analyze_agent import create_analyze_agent, ANALYZE_USER_PROMPT
from llm.action_agent import create_action_agent, ACTION_USER_PROMPT
from llm.validate_agent import create_validate_agent, VALIDATE_USER_PROMPT
from llm.conclusion_agent import create_conclusion_agent
from libs.vector_search import get_manual_documents, format_context_from_docs

router = APIRouter()

@router.post("/api/identify")
async def identify_problem(request: Annotated[IdentifyProblemForm, Form()]):
    session = SQLiteSession(request.session_id, "conversations.db")
    user_input = IDENTIFY_USER_PROMPT.format(error_message=request.query)

    result = await Runner.run(create_identify_agent, user_input, session=session)

    return result.final_output

@router.post("/api/locating")
async def locating_problem(request: Annotated[LocatingProblemForm, Form()], vector_store=Depends(get_vector_store)):
    session = SQLiteSession(request.session_id, "conversations.db")
    manuals = get_manual_documents(query=request.problem_interpretation, k=3, vector_store=vector_store)
    user_input = LOCATING_USER_PROMPT.format(manual=format_context_from_docs(manuals))
    result = await Runner.run(create_locating_agent, user_input, session=session)
    return result.final_output

@router.post("/api/analyze")
async def analyze_problem(request: Annotated[AnalyzeProblemForm, Form()], vector_store=Depends(get_vector_store)):
    session = SQLiteSession(request.session_id, "conversations.db")
    manuals = get_manual_documents(query=request.problem_interpretation, k=3, vector_store=vector_store)
    user_input = ANALYZE_USER_PROMPT.format(locating_response=request.locating_response, manual=format_context_from_docs(manuals))
    result = await Runner.run(create_analyze_agent, user_input, session=session)
    return result.final_output

@router.post("/api/action")
async def action_for_problem(request: Annotated[ActionProblemForm, Form()], vector_store=Depends(get_vector_store)):
    session = SQLiteSession(request.session_id, "conversations.db")
    manuals = get_manual_documents(query=request.root_cause, k=3, vector_store=vector_store)
    user_input = ACTION_USER_PROMPT.format(root_cause=request.root_cause, manual=format_context_from_docs(manuals))
    result = await Runner.run(create_action_agent, user_input, session=session)
    return result.final_output

@router.post("/api/validate")
async def validate_action(request: Annotated[ValidateActionForm, Form()], vector_store=Depends(get_vector_store)):
    session = SQLiteSession(request.session_id, "conversations.db")
    manuals = get_manual_documents(query=request.root_cause, k=3, vector_store=vector_store)
    user_input = VALIDATE_USER_PROMPT.format(
        root_cause=request.root_cause,
        problem_interpretation=request.problem_interpretation,
        manual=format_context_from_docs(manuals)
    )
    result = await Runner.run(create_validate_agent, user_input, session=session)
    return result.final_output

@router.post("/api/conclusion")
async def conclusion(request: Annotated[ConclusionForm, Form()]):
    session = SQLiteSession(request.session_id, "conversations.db")
    result = await Runner.run(create_conclusion_agent, "", session=session)
    return result.final_output