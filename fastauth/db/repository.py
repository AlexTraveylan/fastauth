from collections.abc import Sequence

from sqlalchemy.exc import NoResultFound
from sqlmodel import Session, select

from fastauth.common.exceptions import NotFoundException


class Repository[T]:
    """Repository pattern for database operations.

    Exemple for User, when user is a SQLModel:
    >>> class UserRepository(Repository[User]):
    >>>     __model__ = User
    """

    __model__: type[T]

    @staticmethod
    def create(session: Session, item: T) -> T:
        """Create an item in the database."""
        session.add(item)
        session.flush()

        return item

    def update(self, session: Session, id_: int, **kwargs) -> T:
        """Update an item in the database."""
        bd_item = session.get_one(self.__model__, id_)

        for key, value in kwargs.items():
            setattr(bd_item, key, value)

        session.flush()
        session.refresh(bd_item)

        return bd_item

    def get_or_raise(self, session: Session, **kwargs) -> T:
        """Get an item from the database or raise an error if it doesn't exist."""
        filter_kwargs = [
            getattr(self.__model__, key) == value for key, value in kwargs.items()
        ]

        statement = select(self.__model__).where(*filter_kwargs)
        item = session.exec(statement)

        first_item = item.first()

        if first_item is None:
            raise NotFoundException("No item found")

        return first_item

    def get_or_none(self, session: Session, **kwargs) -> T | None:
        """Get an item from the database or return None if it doesn't exist."""
        filter_kwargs = [
            getattr(self.__model__, key) == value for key, value in kwargs.items()
        ]

        statement = select(self.__model__).where(*filter_kwargs)
        item = session.exec(statement).first()

        return item

    def get_all(self, session: Session) -> Sequence[T]:
        """Get all items from the database."""
        return session.exec(select(self.__model__)).all()

    def delete(self, session: Session, id_: int) -> bool:
        """Delete an item from the database."""
        try:
            item = session.get_one(self.__model__, id_)
        except NoResultFound:
            return False

        session.delete(item)

        return True
