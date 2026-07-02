from datetime import date, datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UpdateUserRequest(BaseModel):
    pass


class CompanyResponse(BaseModel):
    id: UUID
    ticker: str
    name: str
    sector: Optional[str]
    industry: Optional[str]


class LatestPriceResponse(BaseModel):
    ticker: str
    name: str
    sector: Optional[str]
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class PriceBarResponse(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class NoteCreate(BaseModel):
    ticker: str
    date: date
    body: str


class NoteUpdate(BaseModel):
    body: str


class NoteResponse(BaseModel):
    id: UUID
    ticker: str
    company_name: str
    date: date
    body: str
    created_at: datetime
    updated_at: datetime


class AskQuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)


class AskQuestionResponse(BaseModel):
    answer: str
    sql: str
    row_count: int
