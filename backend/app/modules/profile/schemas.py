from pydantic import BaseModel, field_validator
from typing import Dict, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Calibration (mission / onboarding)
# ─────────────────────────────────────────────────────────────────────────────

class CalibrationRequest(BaseModel):
    """
    Payload from the new behavior-driven calibration flow.
    accumulated_scores: summed deltas from scenario + micro questions.
    ab_choice: which format resonated in the A/B test ("visual" | "logical" | "neutral").
    """
    accumulated_scores: Dict[str, float]
    ab_choice: str = "neutral"


# ─────────────────────────────────────────────────────────────────────────────
# FSLSM vector schemas (Phase 4)
# ─────────────────────────────────────────────────────────────────────────────

class FSLSMVector(BaseModel):
    """Current FSLSM state for a user. All values in [-1.0, +1.0]."""
    processing: float = 0.0
    perception: float = 0.0
    reception: float = 0.0
    understanding: float = 0.0

    @field_validator("processing", "perception", "reception", "understanding")
    @classmethod
    def clamp_to_range(cls, v: float) -> float:
        return max(-1.0, min(1.0, v))


class FSLSMNudgeRequest(BaseModel):
    """Deltas to apply to the FSLSM vector. All values are deltas, not absolute."""
    processing: float = 0.0
    perception: float = 0.0
    reception: float = 0.0
    understanding: float = 0.0


class BehavioralSignalsRequest(BaseModel):
    """Alternative: submit a list of predefined behavioral signal names."""
    signals: list[str]


class FSLSMVectorResponse(BaseModel):
    """Full FSLSM state returned to the frontend."""
    processing: float
    perception: float
    reception: float
    understanding: float
    labels: Dict[str, str]  # human-readable labels per dimension


# ─────────────────────────────────────────────────────────────────────────────
# Profile response
# ─────────────────────────────────────────────────────────────────────────────

class ProfileResponse(BaseModel):
    primary_archetype: str
    raw_scores: Dict[str, float]
    learning_sessions_count: int = 0
    fslsm: Optional[FSLSMVector] = None

    class Config:
        from_attributes = True


class ArchetypeOverrideRequest(BaseModel):
    primary_archetype: str
