import uuid
from datetime import date as PyDate

from sqlmodel import Session, select

from backend.database.models import AnnotatedNote, Company
from backend.database.repositories.base import UserScopedRepository


class NoteRepository(UserScopedRepository[AnnotatedNote, uuid.UUID]):
    def __init__(self, session: Session, user_id: uuid.UUID) -> None:
        super().__init__(session, AnnotatedNote, user_id)

    def get_by_company_and_date(self, company_id: uuid.UUID, note_date: PyDate) -> AnnotatedNote | None:
        return self.session.exec(
            select(AnnotatedNote).where(
                AnnotatedNote.user_id == self.user_id,
                AnnotatedNote.company_id == company_id,
                AnnotatedNote.date == note_date,
            )
        ).first()

    def list_with_company(self, company_id: uuid.UUID | None = None) -> list[tuple[AnnotatedNote, Company]]:
        stmt = (
            select(AnnotatedNote, Company)
            .join(Company, AnnotatedNote.company_id == Company.id)
            .where(AnnotatedNote.user_id == self.user_id)
        )
        if company_id is not None:
            stmt = stmt.where(AnnotatedNote.company_id == company_id)
        stmt = stmt.order_by(AnnotatedNote.date.desc())  # type: ignore[attr-defined]
        return list(self.session.exec(stmt).all())
