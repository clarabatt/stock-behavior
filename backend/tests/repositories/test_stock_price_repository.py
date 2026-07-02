import uuid
from datetime import datetime, timedelta, timezone

from sqlmodel import Session

from backend.database.repositories import StockPriceRepository


def test_upsert_batch_inserts_prices(session: Session, CompanyFactory):
    company = CompanyFactory(ticker="AAPL")
    ts = datetime(2026, 7, 2, 14, 30, 0, tzinfo=timezone.utc)
    prices = [
        {
            "id": uuid.uuid4(),
            "company_id": company.id,
            "timestamp": ts,
            "open": 195.0,
            "high": 196.5,
            "low": 194.8,
            "close": 196.2,
            "volume": 1_234_567,
        }
    ]
    StockPriceRepository(session).upsert_batch(prices)
    all_prices = StockPriceRepository(session).list_all()
    assert len(all_prices) == 1
    assert all_prices[0].close == 196.2


def test_upsert_batch_does_not_duplicate_on_conflict(session: Session, CompanyFactory):
    company = CompanyFactory(ticker="AAPL")
    ts = datetime(2026, 7, 2, 14, 30, 0, tzinfo=timezone.utc)
    row = {
        "id": uuid.uuid4(),
        "company_id": company.id,
        "timestamp": ts,
        "open": 195.0,
        "high": 196.5,
        "low": 194.8,
        "close": 196.2,
        "volume": 1_234_567,
    }
    repo = StockPriceRepository(session)
    repo.upsert_batch([row])
    repo.upsert_batch([{**row, "id": uuid.uuid4()}])  # new id, same (company, ts)
    assert len(repo.list_all()) == 1


def test_get_latest_per_company_returns_most_recent(session: Session, CompanyFactory, StockPriceFactory):
    company = CompanyFactory(ticker="AAPL")
    ts_old = datetime(2026, 7, 2, 14, 0, 0, tzinfo=timezone.utc)
    ts_new = datetime(2026, 7, 2, 14, 30, 0, tzinfo=timezone.utc)
    StockPriceFactory(company, timestamp=ts_old, close=100.0)
    StockPriceFactory(company, timestamp=ts_new, close=103.0)

    rows = StockPriceRepository(session).get_latest_per_company()
    assert len(rows) == 1
    _, price = rows[0]
    assert price.close == 103.0


def test_get_latest_per_company_returns_one_row_per_company(session: Session, CompanyFactory, StockPriceFactory):
    aapl = CompanyFactory(ticker="AAPL")
    msft = CompanyFactory(ticker="MSFT")
    ts = datetime(2026, 7, 2, 14, 30, 0, tzinfo=timezone.utc)
    StockPriceFactory(aapl, timestamp=ts, close=196.0)
    StockPriceFactory(msft, timestamp=ts, close=420.0)

    rows = StockPriceRepository(session).get_latest_per_company()
    assert len(rows) == 2


def test_get_latest_per_company_returns_company_info(session: Session, CompanyFactory, StockPriceFactory):
    company = CompanyFactory(ticker="AAPL", name="Apple Inc.", sector="Technology")
    ts = datetime(2026, 7, 2, 14, 30, 0, tzinfo=timezone.utc)
    StockPriceFactory(company, timestamp=ts)

    rows = StockPriceRepository(session).get_latest_per_company()
    returned_company, _ = rows[0]
    assert returned_company.ticker == "AAPL"
    assert returned_company.name == "Apple Inc."


def test_get_history_returns_prices_in_range(session: Session, CompanyFactory, StockPriceFactory):
    company = CompanyFactory(ticker="AAPL")
    base = datetime(2026, 7, 2, 14, 0, 0, tzinfo=timezone.utc)
    for i in range(5):
        StockPriceFactory(company, timestamp=base + timedelta(minutes=5 * i))

    repo = StockPriceRepository(session)
    results = repo.get_history(company.id, base, base + timedelta(minutes=10))
    assert len(results) == 3  # 14:00, 14:05, 14:10


def test_get_history_excludes_other_companies(session: Session, CompanyFactory, StockPriceFactory):
    aapl = CompanyFactory(ticker="AAPL")
    msft = CompanyFactory(ticker="MSFT")
    ts = datetime(2026, 7, 2, 14, 30, 0, tzinfo=timezone.utc)
    StockPriceFactory(aapl, timestamp=ts)
    StockPriceFactory(msft, timestamp=ts)

    results = StockPriceRepository(session).get_history(aapl.id, ts, ts)
    assert len(results) == 1
    assert results[0].company_id == aapl.id
