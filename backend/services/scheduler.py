import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlmodel import Session

from backend.database.session import engine
from backend.services.stock_ingestion import ingest_latest_prices

logger = logging.getLogger(__name__)


def _run_ingestion() -> None:
    with Session(engine) as session:
        ingest_latest_prices(session)


def create_scheduler() -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler()
    scheduler.add_job(_run_ingestion, "interval", minutes=5, id="stock_ingestion", replace_existing=True)
    return scheduler
