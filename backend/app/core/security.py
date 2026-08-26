from fastapi import Header, HTTPException, Depends
from app.core.config import settings

async def verify_internal_api_key(x_internal_token: str = Header(...)):
    if x_internal_token != settings.INTERNAL_API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")