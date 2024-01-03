from sqlalchemy import CheckConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import generic_repr

from .base import IdUuidTimestampedBase
from .constants import COMPETITOR_LABEL_CONSTRAINT
from .tournament_competitor import TournamentCompetitor


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

    tournaments: Mapped[list['Tournament']] = relationship(
        secondary=TournamentCompetitor.__table__,
        back_populates='competitors',
    )
    tournament_associations: Mapped[list[TournamentCompetitor]] = relationship(
        back_populates='competitor',
    )
