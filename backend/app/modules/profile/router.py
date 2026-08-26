from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.profiling.models import UserProfile
from app.modules.profile.schemas import (
    CalibrationRequest,
    ProfileResponse,
    FSLSMVector,
    FSLSMVectorResponse,
    FSLSMNudgeRequest,
    BehavioralSignalsRequest,
    ArchetypeOverrideRequest,
)
from app.modules.auth.schemas import ProfileUpdate
from app.modules.profile.service import calculate_profile
from app.services.fslsm import (
    nudge_vector,
    signals_to_deltas,
    validate_vector,
    default_vector,
    describe_vector,
    DIMENSIONS,
)
from app.core.config import settings

router = APIRouter()


# ─────────────────────────────────────────────────────────────────────────────
# Auth dependencies
# ─────────────────────────────────────────────────────────────────────────────

async def verify_internal_api_key(x_internal_token: str = Header(...)):
    if x_internal_token != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid Internal API Key")


async def get_current_user(
    x_user_email: str = Header(...),
    x_internal_token: str = Header(...),
    db: Session = Depends(get_db),
) -> User:
    await verify_internal_api_key(x_internal_token)
    user = db.query(User).filter(User.email == x_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found in DB")
    return user


def _get_or_create_profile(user: User, db: Session) -> UserProfile:
    if user.profile:
        return user.profile
    profile = UserProfile(
        user_id=user.id,
        primary_archetype="THE_PIONEER",
        raw_scores={"visual": 0, "structural": 0, "active": 0, "logic": 0},
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


# ─────────────────────────────────────────────────────────────────────────────
# Profile endpoints
# ─────────────────────────────────────────────────────────────────────────────

from app.modules.chat.models import ChatSession
from app.modules.content.models import ArticleReading


@router.get("/me", response_model=ProfileResponse)
def get_my_profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    profile = _get_or_create_profile(user, db)

    chat_count = db.query(ChatSession).filter(ChatSession.user_id == user.id).count()
    article_count = db.query(ArticleReading).filter(ArticleReading.user_id == user.id).count()

    fslsm = FSLSMVector(
        processing=profile.fslsm_processing,
        perception=profile.fslsm_perception,
        reception=profile.fslsm_reception,
        understanding=profile.fslsm_understanding,
    )

    return {
        "primary_archetype": profile.primary_archetype,
        "raw_scores": profile.raw_scores or {},
        "learning_sessions_count": chat_count + article_count,
        "fslsm": fslsm,
    }


@router.post("/calibrate")
def submit_calibration(
    data: CalibrationRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    result = calculate_profile(data)
    profile = _get_or_create_profile(user, db)

    profile.primary_archetype = result["primary_archetype"]
    profile.raw_scores = result["raw_scores"]

    # Also seed FSLSM from calibration telemetry
    scores = result["raw_scores"]
    total = sum(scores.values()) or 1
    # Map legacy scores to FSLSM reception and processing dimensions
    profile.fslsm_reception = round(
        ((scores.get("structural", 0) - scores.get("visual", 0)) / 50.0), 3
    )  # more visual → negative (Visual pole)
    profile.fslsm_processing = round(
        ((scores.get("logic", 0) - scores.get("active", 0)) / 50.0), 3
    )  # more active → negative (Active pole)

    db.commit()
    return {"status": "calibrated", "archetype": result["primary_archetype"]}


@router.patch("/override")
def override_archetype(
    data: ArchetypeOverrideRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Allow user to manually override their assigned archetype."""
    profile = _get_or_create_profile(user, db)
    profile.primary_archetype = data.primary_archetype
    db.commit()
    return {"status": "overridden", "archetype": profile.primary_archetype}


@router.post("/update", dependencies=[Depends(verify_internal_api_key)])
def update_profile(data: ProfileUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = user.profile or UserProfile(user_id=user.id)
    if not user.profile:
        db.add(profile)

    profile.primary_archetype = data.archetype
    profile.raw_scores = data.scores
    db.commit()
    db.refresh(profile)
    return {"status": "updated", "archetype": profile.primary_archetype}


# ─────────────────────────────────────────────────────────────────────────────
# FSLSM endpoints (Phase 4)
# ─────────────────────────────────────────────────────────────────────────────

@router.get("/fslsm", response_model=FSLSMVectorResponse)
def get_fslsm_vector(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return the current FSLSM vector for the authenticated user."""
    profile = _get_or_create_profile(user, db)
    vec = profile.fslsm_vectors
    return FSLSMVectorResponse(
        processing=vec["processing"],
        perception=vec["perception"],
        reception=vec["reception"],
        understanding=vec["understanding"],
        labels=describe_vector(vec),
    )


@router.post("/fslsm/nudge", response_model=FSLSMVectorResponse)
def nudge_fslsm_vector(
    data: FSLSMNudgeRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Apply delta nudges to the user's FSLSM vector.
    All delta values are added to current values and clamped to [-1.0, +1.0].
    """
    profile = _get_or_create_profile(user, db)
    current = profile.fslsm_vectors
    deltas = {
        "processing":    data.processing,
        "perception":    data.perception,
        "reception":     data.reception,
        "understanding": data.understanding,
    }
    updated = nudge_vector(current, deltas)

    profile.fslsm_processing    = updated["processing"]
    profile.fslsm_perception    = updated["perception"]
    profile.fslsm_reception     = updated["reception"]
    profile.fslsm_understanding = updated["understanding"]
    db.commit()

    return FSLSMVectorResponse(
        **updated,
        labels=describe_vector(updated),
    )


@router.post("/fslsm/signals", response_model=FSLSMVectorResponse)
def apply_behavioral_signals(
    data: BehavioralSignalsRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Convert a list of behavioral signal names into FSLSM nudges and apply them.
    Unknown signal names are silently ignored.
    """
    profile = _get_or_create_profile(user, db)
    current = profile.fslsm_vectors
    deltas = signals_to_deltas(data.signals)
    updated = nudge_vector(current, deltas)

    profile.fslsm_processing    = updated["processing"]
    profile.fslsm_perception    = updated["perception"]
    profile.fslsm_reception     = updated["reception"]
    profile.fslsm_understanding = updated["understanding"]
    db.commit()

    return FSLSMVectorResponse(
        **updated,
        labels=describe_vector(updated),
    )


@router.post("/fslsm/reset", response_model=FSLSMVectorResponse)
def reset_fslsm_vector(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Reset the FSLSM vector to neutral (0.0) for all dimensions."""
    profile = _get_or_create_profile(user, db)
    profile.fslsm_processing    = 0.0
    profile.fslsm_perception    = 0.0
    profile.fslsm_reception     = 0.0
    profile.fslsm_understanding = 0.0
    db.commit()

    vec = default_vector()
    return FSLSMVectorResponse(**vec, labels=describe_vector(vec))
