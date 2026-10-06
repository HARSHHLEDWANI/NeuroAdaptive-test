from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class ActivityOut(BaseModel):
    activity_type: str
    concept_ids: list[UUID]
    lesson_id: Optional[UUID]
    reason: str
    score: float
    presentation_format: Optional[str] = None

class RecommendationOut(BaseModel):
    decision_id: UUID
    recommended: ActivityOut
    alternatives: list[ActivityOut]
