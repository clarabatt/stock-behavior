import uuid

import pytest
from sqlmodel import Session

from backend.database.models import User


@pytest.fixture
def UserFactory(session: Session):
    def factory(**kwargs) -> User:
        user = User(
            email=kwargs.get("email", f"user-{uuid.uuid4()}@example.com"),
            google_sub=kwargs.get("google_sub", str(uuid.uuid4())),
            full_name=kwargs.get("full_name", "Test User"),
            picture_url=kwargs.get("picture_url", None),
            is_active=kwargs.get("is_active", True),
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    return factory
