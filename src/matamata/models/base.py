from uuid import UUID, uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import Uuid
from sqlalchemy_utils import Timestamp


class Base(DeclarativeBase):
    pass


class TimestampedBase(Base, Timestamp):
    __abstract__ = True


class IdUuidBase(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    uuid: Mapped[UUID] = mapped_column(Uuid, unique=True, default=uuid4)


class IdUuidTimestampedBase(TimestampedBase, IdUuidBase):
    __abstract__ = True
