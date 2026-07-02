from datetime import date

from fastapi.testclient import TestClient

from backend.database.models import User
from backend.database.repositories import NoteRepository


def test_list_notes_returns_empty_when_no_notes(client: TestClient, dev_user: User):
    response = client.get("/api/notes")
    assert response.status_code == 200
    assert response.json() == []


def test_create_note_persists_and_returns_note(client: TestClient, dev_user: User, CompanyFactory, session):
    company = CompanyFactory(ticker="AAPL", name="Apple Inc.")

    response = client.post(
        "/api/notes",
        json={"ticker": "AAPL", "date": "2026-07-01", "body": "Spike after earnings"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert data["company_name"] == "Apple Inc."
    assert data["date"] == "2026-07-01"
    assert data["body"] == "Spike after earnings"
    assert "id" in data

    persisted = NoteRepository(session, dev_user.id).get_by_company_and_date(company.id, date(2026, 7, 1))
    assert persisted is not None
    assert persisted.body == "Spike after earnings"


def test_create_note_404_for_unknown_ticker(client: TestClient, dev_user: User):
    response = client.post(
        "/api/notes",
        json={"ticker": "ZZZZ", "date": "2026-07-01", "body": "Test"},
    )
    assert response.status_code == 404


def test_create_note_409_when_duplicate(client: TestClient, dev_user: User, CompanyFactory, NoteFactory):
    company = CompanyFactory(ticker="AAPL")
    NoteFactory(dev_user, company, date=date(2026, 7, 1))

    response = client.post(
        "/api/notes",
        json={"ticker": "AAPL", "date": "2026-07-01", "body": "Duplicate"},
    )
    assert response.status_code == 409


def test_list_notes_filters_by_ticker(client: TestClient, dev_user: User, CompanyFactory, NoteFactory):
    aapl = CompanyFactory(ticker="AAPL")
    msft = CompanyFactory(ticker="MSFT")
    NoteFactory(dev_user, aapl, date=date(2026, 7, 1))
    NoteFactory(dev_user, msft, date=date(2026, 7, 1))

    response = client.get("/api/notes?ticker=AAPL")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["ticker"] == "AAPL"


def test_update_note_changes_body(client: TestClient, dev_user: User, CompanyFactory, NoteFactory, session):
    company = CompanyFactory(ticker="AAPL")
    note = NoteFactory(dev_user, company, body="Original")

    response = client.patch(f"/api/notes/{note.id}", json={"body": "Updated hypothesis"})

    assert response.status_code == 200
    assert response.json()["body"] == "Updated hypothesis"

    session.expire(note)
    session.refresh(note)
    assert note.body == "Updated hypothesis"


def test_update_note_404_for_unknown_id(client: TestClient, dev_user: User):
    import uuid
    response = client.patch(f"/api/notes/{uuid.uuid4()}", json={"body": "Ghost"})
    assert response.status_code == 404


def test_delete_note_removes_it(client: TestClient, dev_user: User, CompanyFactory, NoteFactory, session):
    company = CompanyFactory(ticker="AAPL")
    note = NoteFactory(dev_user, company)

    response = client.delete(f"/api/notes/{note.id}")
    assert response.status_code == 204

    remaining = NoteRepository(session, dev_user.id).list_with_company()
    assert len(remaining) == 0


def test_delete_note_404_for_unknown_id(client: TestClient, dev_user: User):
    import uuid
    response = client.delete(f"/api/notes/{uuid.uuid4()}")
    assert response.status_code == 404
