from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.auth.models import User
from app.modules.profiling.models import UserProfile
from app.modules.auth.schemas import UserSync
from app.core.config import settings

router = APIRouter()

# --- Security Dependency ---
async def verify_internal_api_key(x_internal_token: str = Header(...)):
    if x_internal_token != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")

# --- Sync Endpoint ---
# FIXED: Added the dependency to protect this endpoint from the public internet
@router.post("/sync", dependencies=[Depends(verify_internal_api_key)])
def sync_user(user_data: UserSync, db: Session = Depends(get_db)):
    # 1. Check if user exists
    user = db.query(User).filter(User.email == user_data.email).first()
    
    if not user:
        # 2. If new, create User + Empty Profile
        new_user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=None, # FIXED: Replaced the "oauth_user" string hack
            is_active=True
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        # Create empty profile
        new_profile = UserProfile(user_id=new_user.id)
        db.add(new_profile)
        db.commit()
        
        return {"status": "created", "user_id": new_user.id}
    
    return {"status": "exists", "user_id": user.id}

