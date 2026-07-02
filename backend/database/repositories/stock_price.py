import uuid
from datetime import datetime

from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert
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
        subq = (
            select(StockPrice.company_id, func.max(StockPrice.timestamp).label("max_ts"))
            .group_by(StockPrice.company_id)
            .subquery()
        )
        stmt = (
            select(Company, StockPrice)
            .join(StockPrice, Company.id == StockPrice.company_id)
            .join(
                subq,
                (StockPrice.company_id == subq.c.company_id)
                & (StockPrice.timestamp == subq.c.max_ts),
            )
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
