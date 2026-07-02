import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pandas as pd
import pytest
from sqlmodel import Session

from backend.database.repositories import StockPriceRepository
from backend.services.stock_ingestion import ingest_latest_prices, is_market_open


def _make_price_df(ts: pd.Timestamp) -> pd.DataFrame:
    return pd.DataFrame(
        {"Open": [195.0], "High": [196.5], "Low": [194.8], "Close": [196.2], "Volume": [1_234_567]},
        index=pd.DatetimeIndex([ts], tz="UTC"),
    )


def _make_multi_ticker_df(tickers: list[str], ts: pd.Timestamp) -> pd.DataFrame:
    frames = {ticker: _make_price_df(ts) for ticker in tickers}
    return pd.concat(frames, axis=1)


# ── market hours guard ──────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "iso_time,expected",
    [
        ("2026-07-02 09:30:00-04:00", True),   # market open (ET)
        ("2026-07-02 15:59:00-04:00", True),   # just before close
        ("2026-07-02 16:00:00-04:00", True),   # exactly at close
        ("2026-07-02 09:29:00-04:00", False),  # one minute before open
        ("2026-07-02 16:01:00-04:00", False),  # after close
        ("2026-07-04 12:00:00-04:00", False),  # Saturday
        ("2026-07-05 12:00:00-04:00", False),  # Sunday
    ],
)
def test_is_market_open(iso_time: str, expected: bool):
    import pytz
    from datetime import datetime as dt
    et = pytz.timezone("America/New_York")
    fake_now = dt.fromisoformat(iso_time).astimezone(et)
    with patch("backend.services.stock_ingestion.datetime") as mock_dt:
        mock_dt.now.return_value = fake_now
        assert is_market_open() == expected


# ── ingestion ───────────────────────────────────────────────────────────────

def test_ingest_latest_prices_stores_rows(session: Session, CompanyFactory):
    company = CompanyFactory(ticker="AAPL")
    ts = pd.Timestamp("2026-07-02 14:30:00", tz="UTC")
    mock_df = _make_multi_ticker_df(["AAPL"], ts)

    with (
        patch("backend.services.stock_ingestion.is_market_open", return_value=True),
        patch("backend.services.stock_ingestion.yf.download", return_value=mock_df),
    ):
        count = ingest_latest_prices(session)

    assert count == 1
    prices = StockPriceRepository(session).list_all()
    assert len(prices) == 1
    assert prices[0].company_id == company.id
    assert prices[0].close == 196.2


def test_ingest_latest_prices_is_idempotent(session: Session, CompanyFactory):
    CompanyFactory(ticker="AAPL")
    ts = pd.Timestamp("2026-07-02 14:30:00", tz="UTC")
    mock_df = _make_multi_ticker_df(["AAPL"], ts)

    with (
        patch("backend.services.stock_ingestion.is_market_open", return_value=True),
        patch("backend.services.stock_ingestion.yf.download", return_value=mock_df),
    ):
        ingest_latest_prices(session)
        ingest_latest_prices(session)

    assert len(StockPriceRepository(session).list_all()) == 1


def test_ingest_skips_when_market_closed(session: Session, CompanyFactory):
    CompanyFactory(ticker="AAPL")

    with (
        patch("backend.services.stock_ingestion.is_market_open", return_value=False),
        patch("backend.services.stock_ingestion.yf.download") as mock_download,
    ):
        count = ingest_latest_prices(session)

    mock_download.assert_not_called()
    assert count == 0
    assert len(StockPriceRepository(session).list_all()) == 0


def test_ingest_skips_when_no_companies(session: Session):
    with (
        patch("backend.services.stock_ingestion.is_market_open", return_value=True),
        patch("backend.services.stock_ingestion.yf.download") as mock_download,
    ):
        count = ingest_latest_prices(session)

    mock_download.assert_not_called()
    assert count == 0
