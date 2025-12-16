from typing import Optional
from pydantic import BaseModel, Field

class GuideBasisItem(BaseModel):
    start_page: str = Field(..., description="Starting page of the referenced guide chunk")
    last_page: str = Field(..., description="Ending page of the referenced guide chunk")
    chapter: str = Field(..., description="Chapter or section title of the referenced guide chunk")
    note: Optional[str] = Field(
        default=None,
        description="What this reference is used for (e.g., 'safety check', 'test procedure', 'decision criteria')"
    )