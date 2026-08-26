from app.modules.profile.schemas import CalibrationRequest

_DIMS = ("visual", "structural", "active", "logic")
_BASELINE = 15.0  # starting score for every dimension before deltas are applied

_ARCHETYPE_MAP = {
    "visual":      "THE_VISUALIZER",
    "structural":  "THE_ARCHITECT",
    "active":      "THE_SPRINTER",
    "logic":       "THE_DEBUGGER",
}

_AB_DELTAS: dict[str, dict[str, float]] = {
    "visual":  {"visual": 5.0},
    "logical": {"logic": 5.0},
}


def calculate_profile(data: CalibrationRequest) -> dict:
    """
    Compute raw_scores and primary_archetype from calibration input.

    Strategy:
    - Start every dimension at _BASELINE (15).
    - Add the client-accumulated deltas (scenario + micro questions).
    - Apply A/B choice bonus.
    - Clamp each dimension to [0, 100].
    - Pick the archetype as the highest-scoring dimension.
    """
    scores: dict[str, float] = {dim: _BASELINE for dim in _DIMS}

    # Accumulate scenario + micro deltas sent from the frontend
    for dim, val in data.accumulated_scores.items():
        if dim in scores:
            scores[dim] += float(val)

    # Apply A/B bonus
    for dim, delta in _AB_DELTAS.get(data.ab_choice, {}).items():
        scores[dim] = scores.get(dim, _BASELINE) + delta

    # Clamp to [0, 100]
    for dim in _DIMS:
        scores[dim] = max(0.0, min(100.0, scores[dim]))

    winner = max(scores, key=scores.__getitem__)
    archetype = _ARCHETYPE_MAP.get(winner, "THE_PIONEER")

    return {"primary_archetype": archetype, "raw_scores": scores}
