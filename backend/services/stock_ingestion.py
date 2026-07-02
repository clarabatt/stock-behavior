import logging
import uuid
from datetime import datetime, timezone

import io

import httpx
import pandas as pd
import pytz
import yfinance as yf
from sqlmodel import Session

from backend.database.repositories import CompanyRepository, StockPriceRepository

logger = logging.getLogger(__name__)

_ET = pytz.timezone("America/New_York")
SP500_COMPANIES_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def fetch_sp500_companies() -> list[dict]:
    headers = {"User-Agent": "stock-behavior/1.0 (https://github.com/stock-behavior; educational use)"}
    response = httpx.get(SP500_COMPANIES_URL, headers=headers, follow_redirects=True, timeout=30)
    response.raise_for_status()
    df = pd.read_html(io.StringIO(response.text), attrs={"id": "constituents"})[0]
    return [
        {
            "id": uuid.uuid4(),
            "ticker": str(row["Symbol"]).replace(".", "-"),
            "name": str(row["Security"]),
            "sector": str(row["GICS Sector"]),
            "industry": str(row["GICS Sub-Industry"]),
            "is_active": True,
        }
        for _, row in df.iterrows()
    ]


def is_market_open() -> bool:
    now = datetime.now(_ET)
    if now.weekday() >= 5:
        return False
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    return market_open <= now <= market_close


def ingest_latest_prices(session: Session, force: bool = False, period: str = "1d") -> int:
    if not force and not is_market_open():
        logger.debug("Market closed, skipping ingestion")
        return 0

    company_repo = CompanyRepository(session)
    price_repo = StockPriceRepository(session)

    companies = company_repo.get_all_active()
    if not companies:
        logger.warning("No active companies found, skipping ingestion")
        return 0

    tickers = [c.ticker for c in companies]
    ticker_to_id = {c.ticker: c.id for c in companies}

    logger.info("Fetching 5m prices (%s) for %d tickers", period, len(tickers))
    raw = yf.download(
        tickers,
        period=period,
        interval="5m",
        group_by="ticker",
        auto_adjust=True,
        progress=False,
    )

    prices: list[dict] = []
    for ticker in tickers:
        try:
            df: pd.DataFrame = raw[ticker] if isinstance(raw.columns, pd.MultiIndex) else raw
        except KeyError:
            continue

        company_id = ticker_to_id[ticker]
        for ts, row in df.iterrows():
            if pd.isna(row["Close"]):
                continue
            prices.append(
                {
                    "id": uuid.uuid4(),
                    "company_id": company_id,
                    "timestamp": pd.Timestamp(ts).tz_convert("UTC").to_pydatetime(),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]),
                }
            )

    price_repo.upsert_batch(prices)
    logger.info("Ingested %d price rows", len(prices))
    return len(prices)
