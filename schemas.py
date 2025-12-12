from typing import Optional
from fastapi import File, UploadFile
from pydantic import BaseModel, Field, field_validator


class JobBoardForm(BaseModel):
  slug: str = Field(..., min_length=3, max_length=20)
  logo: UploadFile = File(...)

  # @field_validator("slug")
  # @classmethod
  # def to_lowercase(cls, v):
  #   return v.lower()
  
class JobBoardPatchForm(BaseModel):
  slug: Optional[str] = Field(None, min_length=3, max_length=20)
  logo: Optional[UploadFile] = File(None)

  # @field_validator("slug")
  # @classmethod
  # def to_lowercase(cls, v):
  #   return v.lower()
  
class JobApplicationForm(BaseModel):
  job_post_id: int
  first_name: str = Field(..., min_length=1, max_length=20)
  last_name: str = Field(..., min_length=1, max_length=20)
  email: str = Field(..., min_length=1, max_length=30)
  resume: UploadFile = File(...)

class JobPostForm(BaseModel):
  job_board_id: int
  title: str = Field(..., min_length=1, max_length=100)
  description: str = Field(..., min_length=1, max_length=2000)

class AdminLoginForm(BaseModel):
  username : str
  password : str

class ReviewDiscriptionForm(BaseModel):
  description: str