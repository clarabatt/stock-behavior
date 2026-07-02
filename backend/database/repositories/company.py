import uuid
from typing import Optional

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import Session, select

from backend.database.models import Company
from backend.database.repositories.base import BaseRepository


class CompanyRepository(BaseRepository[Company, uuid.UUID]):
    def __init__(self, session: Session) -> None:
        super().__init__(session, Company)

    def get_by_ticker(self, ticker: str) -> Optional[Company]:
        return self.session.exec(select(Company).where(Company.ticker == ticker)).first()

    def get_all_active(self) -> list[Company]:
        return list(self.session.exec(select(Company).where(Company.is_active == True)).all())

    def upsert_all(self, companies: list[dict]) -> None:
        if not companies:
            return
        for c in companies:
            c.setdefault("id", uuid.uuid4())
            c.setdefault("is_active", True)
        stmt = pg_insert(Company).values(companies)
        stmt = stmt.on_conflict_do_update(
            index_elements=["ticker"],
            set_={
                "name": stmt.excluded.name,
                "sector": stmt.excluded.sector,
                "industry": stmt.excluded.industry,
            },
        )
        self.session.execute(stmt)
        self.session.commit()
