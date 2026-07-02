import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.types import Scope

logger = logging.getLogger(__name__)


class SPAStaticFiles(StaticFiles):
    async def get_response(self, path: str, scope: Scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as ex:
            if ex.status_code == 404:
                return await super().get_response("index.html", scope)
            raise

from backend.config import settings
from backend.database.repositories import CompanyRepository
from backend.database.session import engine
from backend.routers import auth, users, dev, stocks
from backend.services.scheduler import create_scheduler
from backend.services.stock_ingestion import fetch_sp500_companies


@asynccontextmanager
async def lifespan(app: FastAPI):
    with Session(engine) as session:
        repo = CompanyRepository(session)
        if not repo.get_all_active():
            logger.info("Seeding S&P 500 company list")
            try:
                companies = fetch_sp500_companies()
                repo.upsert_all(companies)
                logger.info("Seeded %d companies", len(companies))
            except Exception:
                logger.exception("Failed to seed companies")

    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Scheduler started")

    yield

    scheduler.shutdown()
    logger.info("Scheduler stopped")


app = FastAPI(title="Stock Behavior", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(stocks.router, prefix="/api", tags=["stocks"])

if settings.dev_mode:
    app.include_router(dev.router, prefix="/api/dev", tags=["dev"])


@app.get("/health")
def health():
    return {"status": "ok"}


frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", SPAStaticFiles(directory=str(frontend_dist), html=True), name="frontend")
