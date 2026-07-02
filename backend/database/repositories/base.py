import uuid
from typing import Generic, Optional, Type, TypeVar

from sqlmodel import Session, SQLModel, select

T = TypeVar("T", bound=SQLModel)
ID = TypeVar("ID")


class BaseRepository(Generic[T, ID]):
    def __init__(self, session: Session, model: Type[T]) -> None:
        self.session = session
        self.model = model

    def get_by_id(self, id: ID) -> Optional[T]:
        return self.session.get(self.model, id)

    def list_all(self) -> list[T]:
        return list(self.session.exec(select(self.model)).all())

    def add(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def update(self, obj: T) -> T:
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def delete(self, obj: T) -> None:
        self.session.delete(obj)
        self.session.commit()


class UserScopedRepository(BaseRepository[T, ID]):
    """Base for repositories whose model has a user_id column.

    get_by_id and list_all are automatically filtered to self.user_id.
    """

    def __init__(self, session: Session, model: Type[T], user_id: uuid.UUID) -> None:
        super().__init__(session, model)
        self.user_id = user_id

    def get_by_id(self, id: ID) -> Optional[T]:
        return self.session.exec(
            select(self.model).where(
                self.model.id == id,  # type: ignore[attr-defined]
                self.model.user_id == self.user_id,  # type: ignore[attr-defined]
            )
        ).first()

    def list_all(self) -> list[T]:
        return list(
            self.session.exec(
                select(self.model).where(self.model.user_id == self.user_id)  # type: ignore[attr-defined]
            ).all()
        )
