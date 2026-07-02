import uuid
from datetime import date as PyDate
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, DateTime, Text, UniqueConstraint
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
    full_name: str
    picture_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    is_active: bool = Field(default=True)


class AnnotatedNote(SQLModel, table=True):
    __tablename__ = "annotated_notes"
    __table_args__ = (
        UniqueConstraint("user_id", "company_id", "date", name="uq_notes_user_company_date"),
    )

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", index=True)
    company_id: uuid.UUID = Field(foreign_key="companies.id", index=True)
    date: PyDate = Field(index=True)
    body: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


