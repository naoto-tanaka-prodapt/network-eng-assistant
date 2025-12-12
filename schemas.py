from typing import Optional
from fastapi import File, UploadFile
from pydantic import BaseModel, Field, field_validator


class CreateProcedureForm(BaseModel):
  query: str = Field(..., min_length=3)