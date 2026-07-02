import logging
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session

from backend.database.session import engine
from backend.services.stock_ingestion import ingest_latest_prices

logger = logging.getLogger(__name__)


def _run_initial() -> None:
    with Session(engine) as session:
        ingest_latest_prices(session, force=True, period="60d")


def _run_periodic() -> None:
    with Session(engine) as session:
        ingest_latest_prices(session)


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(_run_initial, "date", run_date=datetime.now(), id="stock_ingestion_initial")
    scheduler.add_job(_run_periodic, "interval", minutes=5, id="stock_ingestion")
    return scheduler
