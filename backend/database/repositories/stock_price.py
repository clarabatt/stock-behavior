import uuid
from datetime import datetime

from sqlalchemy import true
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import aliased
from sqlmodel import Session, select

from backend.database.models import Company, StockPrice
from backend.database.repositories.base import BaseRepository


class StockPriceRepository(BaseRepository[StockPrice, uuid.UUID]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, StockPrice)

    def upsert_batch(self, prices: list[dict]) -> None:
        if not prices:
            return
        for p in prices:
            p.setdefault("id", uuid.uuid4())
        stmt = pg_insert(StockPrice).values(prices)
        stmt = stmt.on_conflict_do_nothing(constraint="uq_stock_prices_company_timestamp")
        self.session.execute(stmt)
        self.session.commit()

    def get_latest_per_company(self) -> list[tuple[Company, StockPrice]]:
        latest_subq = (
            select(StockPrice)
            .where(StockPrice.company_id == Company.id)
            .order_by(StockPrice.timestamp.desc())
            .limit(1)
            .correlate(Company)
            .subquery()
            .lateral()
        )
        sp = aliased(StockPrice, latest_subq)
        stmt = (
            select(Company, sp)
            .join(sp, true())
            .order_by(Company.ticker)
        )
        return list(self.session.exec(stmt).all())

    def get_history(
        self, company_id: uuid.UUID, from_dt: datetime, to_dt: datetime
    ) -> list[StockPrice]:
        stmt = (
            select(StockPrice)
            .where(
                StockPrice.company_id == company_id,
                StockPrice.timestamp >= from_dt,
                StockPrice.timestamp <= to_dt,
            )
            .order_by(StockPrice.timestamp)
        )
        return list(self.session.exec(stmt).all())
