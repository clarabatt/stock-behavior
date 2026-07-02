from fastapi import APIRouter, Depends

from backend.services.auth import get_current_user
from backend.config import settings
from backend.database.models import User

router = APIRouter()


@router.get("/me")
async def get_me(user: User = Depends(get_current_user)):
    return {
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "picture_url": user.picture_url,
            "is_admin": user.email == settings.admin_email and bool(settings.admin_email),
        }
    }
