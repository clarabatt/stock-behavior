from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from backend.database.repositories import CompanyRepository, StockPriceRepository
from backend.database.session import get_session
from backend.schemas import CompanyResponse, LatestPriceResponse, PriceBarResponse

router = APIRouter()


@router.get("/companies", response_model=list[CompanyResponse])
def list_companies(session: Session = Depends(get_session)) -> list[CompanyResponse]:
    companies = CompanyRepository(session).get_all_active()
    return [
        CompanyResponse(
            id=c.id,
            ticker=c.ticker,
            name=c.name,
            sector=c.sector,
            industry=c.industry,
        )
        for c in companies
    ]


@router.get("/prices/latest", response_model=list[LatestPriceResponse])
def latest_prices(session: Session = Depends(get_session)) -> list[LatestPriceResponse]:
    rows = StockPriceRepository(session).get_latest_per_company()
    return [
        LatestPriceResponse(
            ticker=company.ticker,
            name=company.name,
            sector=company.sector,
            timestamp=price.timestamp,
            open=price.open,
            high=price.high,
            low=price.low,
            close=price.close,
            volume=price.volume,
        )
        for company, price in rows
    ]


@router.get("/prices/{ticker}/history", response_model=list[PriceBarResponse])
def price_history(
    ticker: str,
    from_dt: datetime = Query(..., alias="from"),
    to_dt: datetime = Query(..., alias="to"),
    session: Session = Depends(get_session),
) -> list[PriceBarResponse]:
    company = CompanyRepository(session).get_by_ticker(ticker.upper())
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")
    prices = StockPriceRepository(session).get_history(company.id, from_dt, to_dt)
    return [
        PriceBarResponse(
            timestamp=p.timestamp,
            open=p.open,
            high=p.high,
            low=p.low,
            close=p.close,
            volume=p.volume,
        )
        for p in prices
    ]
