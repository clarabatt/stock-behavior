from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


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
