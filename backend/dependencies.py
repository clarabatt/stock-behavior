from fastapi import Depends, HTTPException

from backend.services.auth import get_current_user
from backend.config import settings
from backend.database.models import User


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not settings.admin_email or user.email != settings.admin_email:
        raise HTTPException(status_code=403, detail="Forbidden")
    return user
