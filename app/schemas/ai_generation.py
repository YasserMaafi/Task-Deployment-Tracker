from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AIGenerationResponse(BaseModel):
    id: int
    project_id: int
    user_id: Optional[int]
    generation_type: str
    input_payload: dict
    output_content: Optional[str]
    model_used: Optional[str]
    status: str
    error_message: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True
