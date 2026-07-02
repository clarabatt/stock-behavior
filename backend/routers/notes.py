from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from backend.database.models import User
from backend.database.repositories import CompanyRepository, NoteRepository
from backend.database.session import get_session
from backend.schemas import NoteCreate, NoteResponse, NoteUpdate
from backend.services.auth import get_current_user

router = APIRouter()


def _to_response(note, company) -> NoteResponse:
    return NoteResponse(
        id=note.id,
        ticker=company.ticker,
        company_name=company.name,
        date=note.date,
        body=note.body,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.get("/notes", response_model=list[NoteResponse])
def list_notes(
    ticker: str | None = Query(default=None),
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[NoteResponse]:
    company_id = None
    if ticker is not None:
        company = CompanyRepository(session).get_by_ticker(ticker.upper())
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        company_id = company.id

    repo = NoteRepository(session, user.id)
    rows = repo.list_with_company(company_id)
    return [_to_response(note, company) for note, company in rows]


@router.post("/notes", response_model=NoteResponse, status_code=201)
def create_note(
    body: NoteCreate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> NoteResponse:
    company = CompanyRepository(session).get_by_ticker(body.ticker.upper())
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    repo = NoteRepository(session, user.id)
    existing = repo.get_by_company_and_date(company.id, body.date)
    if existing is not None:
        raise HTTPException(status_code=409, detail="Note already exists for this date")

    from backend.database.models import AnnotatedNote

    note = repo.add(
        AnnotatedNote(
            user_id=user.id,
            company_id=company.id,
            date=body.date,
            body=body.body,
        )
    )
    return _to_response(note, company)


@router.patch("/notes/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: UUID,
    body: NoteUpdate,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> NoteResponse:
    repo = NoteRepository(session, user.id)
    note = repo.get_by_id(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")

    note.body = body.body
    note.updated_at = datetime.utcnow()
    note = repo.update(note)

    company = CompanyRepository(session).get_by_id(note.company_id)
    return _to_response(note, company)


@router.delete("/notes/{note_id}", status_code=204)
def delete_note(
    note_id: UUID,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    repo = NoteRepository(session, user.id)
    note = repo.get_by_id(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    repo.delete(note)
