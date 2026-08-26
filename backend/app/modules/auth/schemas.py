from pydantic import BaseModel
from typing import Dict, Any, Optional  # <--- Import Optional

class UserSync(BaseModel):
    email: str
    full_name: Optional[str] = None     # <--- Change 'str | None' to 'Optional[str]'
    provider_id: Optional[str] = None

class ProfileUpdate(BaseModel):
    user_email: str
    archetype: str          
    scores: Dict[str, Any]