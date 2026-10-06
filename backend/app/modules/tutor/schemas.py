from typing import Literal
from uuid import UUID
from pydantic import BaseModel

class CitationOut(BaseModel):
    claim: str
    chunk_id: str
    validation_status: str

class LessonContentOut(BaseModel):
    content_markdown: str
    citations: list[CitationOut]
    grounding_mode: str
    retrieved_chunk_ids: list[str]

class TutorRetrieval(BaseModel):
    chunk_ids: list[str]

class TutorToken(BaseModel):
    text: str

class TutorDone(BaseModel):
    message_id: UUID
    grounding_mode: str
    token_usage: dict[str, str]

class TutorInsufficient(BaseModel):
    message_id: UUID
    text: str

class TutorEvent(BaseModel):
    event: Literal["retrieval", "token", "citation", "done", "insufficient"]
    data: TutorRetrieval | TutorToken | CitationOut | TutorDone | TutorInsufficient
