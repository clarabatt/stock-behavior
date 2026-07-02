import uuid
from datetime import datetime, timezone

import pytest
from sqlmodel import Session

from backend.database.models import Company, StockPrice, User


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


@pytest.fixture
def CompanyFactory(session: Session):
    def factory(**kwargs) -> Company:
        company = Company(
            ticker=kwargs.get("ticker", f"T{str(uuid.uuid4())[:4].upper()}"),
            name=kwargs.get("name", "Test Corp"),
            sector=kwargs.get("sector", "Technology"),
            industry=kwargs.get("industry", "Software"),
            is_active=kwargs.get("is_active", True),
        )
        session.add(company)
        session.commit()
        session.refresh(company)
        return company

    return factory


@pytest.fixture
def StockPriceFactory(session: Session):
    def factory(company: Company, **kwargs) -> StockPrice:
        price = StockPrice(
            company_id=company.id,
            timestamp=kwargs.get("timestamp", datetime(2026, 7, 2, 14, 30, 0, tzinfo=timezone.utc)),
            open=kwargs.get("open", 100.0),
            high=kwargs.get("high", 105.0),
            low=kwargs.get("low", 99.0),
            close=kwargs.get("close", 103.0),
            volume=kwargs.get("volume", 1_000_000),
        )
        session.add(price)
        session.commit()
        session.refresh(price)
        return price

    return factory
