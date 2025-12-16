from typing import List, Optional
from fastapi import File, UploadFile
from pydantic import BaseModel, Field, field_validator


class CreateProcedureForm(BaseModel):
  query: str = Field(..., min_length=3)

class IdentifyProblemForm(BaseModel):
  query: str = Field(..., min_length=3)
  session_id: str = Field(..., min_length=3)

class LocatingProblemForm(BaseModel):
  session_id: str = Field(..., min_length=3)
  facts: str = Field(..., min_length=3)
  media_hint: str = Field(...)
  keywords: str = Field(..., min_length=3) # カンマ区切り

class AnalyzeProblemForm(BaseModel):
  session_id: str = Field(..., min_length=3)
  facts: str = Field(..., min_length=3)
  locating_response: str = Field(..., min_length=3)

class ActionProblemForm(BaseModel):
  session_id: str = Field(..., min_length=3)
  root_cause: str = Field(..., min_length=3)

class ValidateActionForm(BaseModel):
  session_id: str = Field(..., min_length=3)
  problem_interpretation: str = Field(..., min_length=3)
  root_cause: str = Field(..., min_length=3)

class ConclusionForm(BaseModel):
  session_id: str = Field(..., min_length=3)