from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel import Session, select

from backend.services.auth import create_session_token
from backend.database.models import User
from backend.database.session import get_session

router = APIRouter()

DEV_EMAIL = "dev@stock.local"


@router.post("/login")
def dev_login(session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == DEV_EMAIL)).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"Seed user {DEV_EMAIL!r} not found — run `make seed` first",
        )

    token = create_session_token(str(user.id))
    response = JSONResponse({"ok": True, "user": user.email})
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        samesite="lax",
        max_age=60 * 60 * 24 * 30,
    )
    return response
