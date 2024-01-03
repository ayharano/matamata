from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_utils import Timestamp


class Base(DeclarativeBase):
    pass


class TimestampedBase(Base, Timestamp):
    __abstract__ = True
