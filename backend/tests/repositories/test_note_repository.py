from datetime import date

from sqlmodel import Session

from backend.database.repositories import NoteRepository


def test_get_by_company_and_date_returns_matching_note(session: Session, UserFactory, CompanyFactory, NoteFactory):
    user = UserFactory()
    company = CompanyFactory()
    NoteFactory(user, company, date=date(2026, 7, 1), body="Note A")

    repo = NoteRepository(session, user.id)
    result = repo.get_by_company_and_date(company.id, date(2026, 7, 1))

    assert result is not None
    assert result.body == "Note A"


def test_get_by_company_and_date_returns_none_for_wrong_date(session: Session, UserFactory, CompanyFactory, NoteFactory):
    user = UserFactory()
    company = CompanyFactory()
    NoteFactory(user, company, date=date(2026, 7, 1))

    repo = NoteRepository(session, user.id)
    result = repo.get_by_company_and_date(company.id, date(2026, 7, 2))

    assert result is None


def test_list_with_company_returns_notes_for_user(session: Session, UserFactory, CompanyFactory, NoteFactory):
    user = UserFactory()
    company = CompanyFactory(ticker="AAPL")
    NoteFactory(user, company, date=date(2026, 7, 1), body="First")
    NoteFactory(user, company, date=date(2026, 7, 2), body="Second")

    repo = NoteRepository(session, user.id)
    rows = repo.list_with_company()

    assert len(rows) == 2
    # ordered by date desc
    assert rows[0][0].body == "Second"
    assert rows[0][1].ticker == "AAPL"


def test_list_with_company_filters_by_company(session: Session, UserFactory, CompanyFactory, NoteFactory):
    user = UserFactory()
    aapl = CompanyFactory(ticker="AAPL")
    msft = CompanyFactory(ticker="MSFT")
    NoteFactory(user, aapl, date=date(2026, 7, 1))
    NoteFactory(user, msft, date=date(2026, 7, 1))

    repo = NoteRepository(session, user.id)
    rows = repo.list_with_company(company_id=aapl.id)

    assert len(rows) == 1
    assert rows[0][1].ticker == "AAPL"


def test_user_scoping_hides_other_users_notes(session: Session, UserFactory, CompanyFactory, NoteFactory):
    user_a = UserFactory()
    user_b = UserFactory()
    company = CompanyFactory()
    NoteFactory(user_a, company, body="User A note")
    NoteFactory(user_b, company, date=date(2026, 7, 3), body="User B note")

    repo_a = NoteRepository(session, user_a.id)
    rows = repo_a.list_with_company()

    assert len(rows) == 1
    assert rows[0][0].body == "User A note"
