"""
Seed the dev database with a test user.

Usage:
    uv run python -m backend.scripts.seed

After running, log in via the dev endpoint:
    curl -X POST http://localhost:8000/api/dev/login
"""

from sqlmodel import Session, select

from backend.database.models import User
from backend.database.session import engine


def seed() -> None:
    with Session(engine) as session:
        user = session.exec(
            select(User).where(User.email == "dev@stock.local")
        ).first()
        if not user:
            user = User(
                email="dev@stock.local",
                google_sub="dev-seed-google-sub-001",
                full_name="Dev User",
                is_active=True,
            )
            session.add(user)
            session.commit()
            print(f"  created user  {user.id}")
        else:
            print(f"  found user    {user.id}")

    print("\nSeed complete")
    print("Log in via: curl -X POST http://localhost:8000/api/dev/login\n")


if __name__ == "__main__":
    seed()
