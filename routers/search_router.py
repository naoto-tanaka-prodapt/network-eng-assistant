from typing import Annotated
from fastapi import APIRouter, Depends, File, UploadFile, Request, Form
from libs.vector_search import get_vector_store
from schemas import CreateProcedureForm
from llm._generate_procedure import generate_procedure


router = APIRouter()

@router.post("/api/create-procedure")
async def review_job_description(request: Annotated[CreateProcedureForm, Form()], vector_store=Depends(get_vector_store)):
    response = generate_procedure(request.query, vector_store) 
    return {"answer": response}