from pydantic import BaseModel, ConfigDict
from typing import List, Optional

class ContextCreateRequest(BaseModel):
    user_id: str
    raw_context: str

class ContextResponse(BaseModel):
    id: str
    problem: Optional[str] = None
    current_progress: Optional[str] = None
    next_step: Optional[str] = None
    open_questions: Optional[List[str]] = None
    notes: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ResumeResponse(BaseModel):
    summary: Optional[str] = None
    next_step: Optional[str] = None
    questions: Optional[List[str]] = None
