from typing import Annotated
from fastapi import APIRouter, File, UploadFile, Request, Form
from schemas import ReviewDiscriptionForm
from llm.review_description import review_description


router = APIRouter()

@router.post("/api/review-job-description")
async def review_job_description(request: Annotated[ReviewDiscriptionForm, Form()]):
    return review_description(request.description)