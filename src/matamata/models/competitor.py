from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import generic_repr

from .base import IdUuidTimestampedBase
from .constants import COMPETITOR_LABEL_CONSTRAINT


@generic_repr
class Competitor(IdUuidTimestampedBase):
    __tablename__ = 'competitor'
    __table_args__ = (
        CheckConstraint(
            "NOT(TRIM(label) LIKE '')",
            name=COMPETITOR_LABEL_CONSTRAINT,
        ),
    )

    label: Mapped[str] = mapped_column(String(255))
