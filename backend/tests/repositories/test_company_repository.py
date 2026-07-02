import uuid

import pytest
from sqlmodel import Session

from backend.database.repositories import CompanyRepository


def test_get_by_ticker_returns_company(session: Session, CompanyFactory):
    company = CompanyFactory(ticker="AAPL", name="Apple Inc.", sector="Technology")
    result = CompanyRepository(session).get_by_ticker("AAPL")
    assert result is not None
    assert result.id == company.id


def test_get_by_ticker_returns_none_for_unknown(session: Session):
    result = CompanyRepository(session).get_by_ticker("ZZZZ")
    assert result is None


def test_get_all_active_excludes_inactive(session: Session, CompanyFactory):
    CompanyFactory(ticker="AAPL", is_active=True)
    CompanyFactory(ticker="DELIST", is_active=False)
    results = CompanyRepository(session).get_all_active()
    tickers = [c.ticker for c in results]
    assert "AAPL" in tickers
    assert "DELIST" not in tickers


def test_upsert_all_inserts_new_companies(session: Session):
    companies = [
        {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Hardware"},
        {"ticker": "MSFT", "name": "Microsoft", "sector": "Technology", "industry": "Software"},
    ]
    CompanyRepository(session).upsert_all(companies)
    results = CompanyRepository(session).get_all_active()
    tickers = {c.ticker for c in results}
    assert {"AAPL", "MSFT"}.issubset(tickers)


def test_upsert_all_updates_existing_company(session: Session, CompanyFactory):
    CompanyFactory(ticker="AAPL", name="Old Name", sector="Old Sector")
    CompanyRepository(session).upsert_all(
        [{"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Hardware"}]
    )
    updated = CompanyRepository(session).get_by_ticker("AAPL")
    assert updated is not None
    assert updated.name == "Apple Inc."
    assert updated.sector == "Technology"


def test_upsert_all_is_idempotent(session: Session):
    companies = [{"ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Hardware"}]
    repo = CompanyRepository(session)
    repo.upsert_all(companies)
    repo.upsert_all(companies)
    results = repo.get_all_active()
    assert len([c for c in results if c.ticker == "AAPL"]) == 1
