from fastapi import Depends
from sqlmodel import Session, select

from backend.database.models import User
from backend.database.session import get_session

DEV_EMAIL = "dev@stock.local"


def get_current_user(session: Session = Depends(get_session)) -> User:
    user = session.exec(select(User).where(User.email == DEV_EMAIL)).first()
    if not user:
        user = User(email=DEV_EMAIL, full_name="Dev User", is_active=True)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user
