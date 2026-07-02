import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, UniqueConstraint
from sqlmodel import Column, Field, SQLModel


class Company(SQLModel, table=True):
    __tablename__ = "companies"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    ticker: str = Field(unique=True, index=True)
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    is_active: bool = Field(default=True)


class StockPrice(SQLModel, table=True):
    __tablename__ = "stock_prices"
    __table_args__ = (UniqueConstraint("company_id", "timestamp", name="uq_stock_prices_company_timestamp"),)

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    company_id: uuid.UUID = Field(foreign_key="companies.id", index=True)
    timestamp: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, index=True))
    open: float
    high: float
    low: float
    close: float
    volume: int = Field(sa_column=Column(BigInteger, nullable=False))


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    google_sub: str = Field(unique=True, index=True)
    full_name: str
    picture_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = Field(default=True)


class OAuthState(SQLModel, table=True):
    __tablename__ = "oauth_states"

    state: str = Field(primary_key=True)
    expires_at: datetime
