from pydantic import BaseModel, Field

class CreateProcedureForm(BaseModel):
  query: str = Field(..., min_length=3)

class IdentifyProblemForm(BaseModel):
  query: str = Field(..., min_length=3)
  session_id: str = Field(..., min_length=3)

class LocatingProblemForm(BaseModel):
  session_id: str = Field(..., min_length=3)
  facts: str = Field(..., min_length=3)
  media_hint: str = Field(...)
  keywords: str = Field(..., min_length=3)

class AnalyzeProblemForm(BaseModel):
  session_id: str = Field(..., min_length=3)
  facts: str = Field(..., min_length=3)
  locating_response: str = Field(..., min_length=3)
  media_hint: str = Field(...)

class ActionProblemForm(BaseModel):
  session_id: str = Field(..., min_length=3)
  root_cause: str = Field(..., min_length=3)
  media_hint: str = Field(...)

class ConclusionForm(BaseModel):
  session_id: str = Field(..., min_length=3)
