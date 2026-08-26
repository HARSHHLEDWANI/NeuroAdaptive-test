# backend/app/modules/profiling/router.py
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.profiling.schemas import CalibrationPayload
from app.modules.profiling.models import UserProfile
from app.modules.auth.models import User # Adjust based on your actual User model import

router = APIRouter(prefix="/api/v1/profile", tags=["profiling"])

@router.post("/calibrate")
def calibrate_user_profile(
    payload: CalibrationPayload,
    x_user_email: str = Header(...),
    x_internal_token: str = Header(...),
    db: Session = Depends(get_db)
):
    # 1. Simple Internal Auth Check
    # In production, check x_internal_token against your environment variable
    if not x_internal_token:
        raise HTTPException(status_code=403, detail="Unauthorized")

    # 2. Find the User
    user = db.query(User).filter(User.email == x_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 3. Find or Create their Profile
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.add(profile)

    tel = payload.telemetry
    quiz = payload.quiz_results

    # --- THE NEUROADAPTIVE MATH ---
    
    # Calculate Visual Affinity
    # Base is time spent, boosted significantly if they got the visual question right
    visual_score = tel.time_spent_on_visuals
    if tel.clicked_diagram:
        visual_score += 10
    if quiz.q3_correct:
        visual_score = int(visual_score * 1.5) # 50% multiplier for effective visual learning

    # Calculate Textual Affinity
    text_score = tel.time_spent_on_text
    if quiz.q1_correct:
        text_score = int(text_score * 1.5)

    # Calculate Depth Preference (Do they want details or summaries?)
    depth_score = 50 # Start neutral
    if tel.read_summary_first:
        depth_score -= 20
    if tel.scrolled_erratically:
        depth_score -= 10
    if tel.time_spent_on_text > 40:
        depth_score += 20
        
    # Assign Archetype based on highest affinities
    if visual_score > text_score and visual_score > 30:
        archetype = "THE_VISUALIZER"
    elif depth_score < 40:
        archetype = "THE_SKIMMER"
    elif text_score > visual_score:
        archetype = "THE_SCHOLAR"
    else:
        archetype = "THE_SYNTHESIZER" # Balanced

    # 4. Update the DB Profile
    profile.visual_affinity = visual_score
    profile.textual_affinity = text_score
    profile.depth_preference = depth_score
    profile.primary_archetype = archetype
    
    # Store the raw payload in the JSON column for future AI fine-tuning
    profile.raw_scores = payload.dict()
    profile.total_engagement_time += (tel.time_spent_on_text + tel.time_spent_on_visuals + tel.time_spent_on_summary)

    db.commit()

    return {"success": True, "archetype": archetype, "message": "Profile calibrated successfully."}