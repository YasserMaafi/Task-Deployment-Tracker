from pydantic import BaseModel
from typing import List, Optional


class ProjectMemberAdd(BaseModel):
    user_id: int


class ProjectMemberRemove(BaseModel):
    user_id: int


class FeedbackCreate(BaseModel):
    feedback_type: str  # note, suggestion, evaluation
    content: str


class FeedbackResponse(BaseModel):
    id: int
    project_id: int
    user_id: Optional[int]
    feedback_type: str
    content: str
    created_at: str
    updated_at: Optional[str]

    class Config:
        from_attributes = True
