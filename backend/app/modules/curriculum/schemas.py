from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class LessonConceptOut(BaseModel):
    concept_id: UUID
    role: str
    weight: float

class LessonOut(BaseModel):
    id: UUID
    title: str
    objective: Optional[str]
    concepts: list[LessonConceptOut]

class ModuleOut(BaseModel):
    id: UUID
    title: str
    lessons: list[LessonOut]

class StructureOut(BaseModel):
    version_id: UUID
    version_number: int
    status: str
    validation_errors: list[str]
    concept_carryover_map: Optional[dict[str, str]]
    modules: list[ModuleOut]

class ConceptOut(BaseModel):
    id: UUID
    canonical_key: str
    name: str
    definition: str
    aliases: list[str]
    importance: float
    bloom_level: Optional[str]

class EdgeOut(BaseModel):
    prerequisite_concept_id: UUID
    dependent_concept_id: UUID
    strength: str
    confidence: float

class GraphOut(BaseModel):
    concepts: list[ConceptOut]
    edges: list[EdgeOut]

class PublishedStructureOut(BaseModel):
    course_id: UUID
    active_version_id: UUID
