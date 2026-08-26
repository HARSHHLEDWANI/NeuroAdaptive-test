"""
FSLSM Vector Math Engine — Phase 2
====================================
Implements the continuous nudge system for Felder-Silverman Learning Style Model.

Dimensions (each -1.0 → +1.0):
  processing:    -1.0 = Active       | +1.0 = Reflective
  perception:    -1.0 = Sensing      | +1.0 = Intuitive
  reception:     -1.0 = Visual       | +1.0 = Verbal
  understanding: -1.0 = Sequential   | +1.0 = Global
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

DIMENSIONS = ("processing", "perception", "reception", "understanding")
MIN_VAL = -1.0
MAX_VAL = 1.0

# ─────────────────────────────────────────────────────────────────────────────
# Core math
# ─────────────────────────────────────────────────────────────────────────────


def clamp(value: float, lo: float = MIN_VAL, hi: float = MAX_VAL) -> float:
    """Clamp a float to [lo, hi]."""
    return max(lo, min(hi, value))


def nudge(current: float, delta: float) -> float:
    """Apply a delta to a dimension value and clamp the result."""
    return clamp(current + delta)


def nudge_vector(current: dict, deltas: dict) -> dict:
    """
    Apply multiple deltas to a vector dict.

    Args:
        current: dict with keys from DIMENSIONS, floats in [-1, 1].
        deltas:  dict with optional keys from DIMENSIONS.

    Returns:
        New vector dict with clamped values.
    """
    result = {dim: float(current.get(dim, 0.0)) for dim in DIMENSIONS}
    for dim, delta in deltas.items():
        if dim in DIMENSIONS:
            result[dim] = nudge(result[dim], float(delta))
    return result


def validate_vector(vec: dict) -> dict:
    """
    Validate and clamp all dimensions of a vector.
    Raises ValueError for unknown keys.
    """
    unknown = set(vec) - set(DIMENSIONS)
    if unknown:
        raise ValueError(f"Unknown FSLSM dimensions: {unknown}")
    return {dim: clamp(float(vec.get(dim, 0.0))) for dim in DIMENSIONS}


def default_vector() -> dict:
    return {dim: 0.0 for dim in DIMENSIONS}


# ─────────────────────────────────────────────────────────────────────────────
# Behavioral signal → delta mapping
# ─────────────────────────────────────────────────────────────────────────────

# Signal names mapped to the FSLSM dimension deltas they produce.
# Negative delta = push toward the left pole; positive = right pole.
BEHAVIORAL_SIGNALS: dict[str, dict] = {
    # Processing dimension
    "tried_example_immediately":   {"processing": -0.10},   # active
    "asked_for_theory_first":      {"processing": +0.10},   # reflective
    "requested_exercise":          {"processing": -0.08},
    "reviewed_notes_before_reply": {"processing": +0.08},

    # Perception dimension
    "asked_for_real_world_example": {"perception": -0.10},  # sensing
    "asked_for_pattern_or_theory":  {"perception": +0.10},  # intuitive
    "preferred_data_over_concept":  {"perception": -0.08},
    "preferred_concept_over_data":  {"perception": +0.08},

    # Reception dimension
    "requested_diagram":           {"reception": -0.12},    # visual
    "ignored_diagram":             {"reception": +0.06},    # verbal
    "requested_text_explanation":  {"reception": +0.10},
    "long_time_on_visual":         {"reception": -0.08},

    # Understanding dimension
    "asked_step_by_step":          {"understanding": -0.10},  # sequential
    "asked_big_picture":           {"understanding": +0.10},  # global
    "skipped_to_end":              {"understanding": +0.12},
    "read_linearly":               {"understanding": -0.08},

    # Quiz performance signals (compound)
    "quiz_got_visual_question":    {"reception": -0.08},
    "quiz_missed_visual_question": {"reception": +0.06},
    "quiz_got_logic_question":     {"processing": +0.06, "understanding": -0.06},
    "quiz_missed_logic_question":  {"processing": -0.06, "understanding": +0.04},
}


def signals_to_deltas(signals: list[str]) -> dict:
    """
    Convert a list of behavioral signal names into a combined delta vector.
    Signals not in BEHAVIORAL_SIGNALS are silently ignored.
    """
    combined: dict[str, float] = {dim: 0.0 for dim in DIMENSIONS}
    for signal in signals:
        if signal in BEHAVIORAL_SIGNALS:
            for dim, delta in BEHAVIORAL_SIGNALS[signal].items():
                combined[dim] += delta
    return combined


# ─────────────────────────────────────────────────────────────────────────────
# Label helpers (for UI / debugging)
# ─────────────────────────────────────────────────────────────────────────────

DimensionPole = Literal[
    "Active", "Reflective",
    "Sensing", "Intuitive",
    "Visual", "Verbal",
    "Sequential", "Global",
    "Neutral",
]

_POLES: dict[str, tuple[str, str]] = {
    "processing":    ("Active", "Reflective"),
    "perception":    ("Sensing", "Intuitive"),
    "reception":     ("Visual", "Verbal"),
    "understanding": ("Sequential", "Global"),
}


def label_dimension(dim: str, value: float, threshold: float = 0.25) -> str:
    """
    Return a human-readable label for a dimension value.

    Example:
        label_dimension("reception", -0.65) → "Visual (strong)"
    """
    left_pole, right_pole = _POLES[dim]
    if value < -threshold:
        strength = "strong" if value < -0.6 else "moderate"
        return f"{left_pole} ({strength})"
    elif value > threshold:
        strength = "strong" if value > 0.6 else "moderate"
        return f"{right_pole} ({strength})"
    return "Balanced"


def describe_vector(vec: dict) -> dict[str, str]:
    """Return human-readable labels for all dimensions."""
    return {dim: label_dimension(dim, float(vec.get(dim, 0.0))) for dim in DIMENSIONS}
