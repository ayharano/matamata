from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import generic_repr

from .base import TimestampedBase


@generic_repr
class TournamentCompetitor(TimestampedBase):
    __tablename__ = 'tournament_competitor'

    tournament_id: Mapped[int] = mapped_column(ForeignKey('tournament.id'), primary_key=True)
    competitor_id: Mapped[int] = mapped_column(ForeignKey('competitor.id'), primary_key=True)

    tournament: Mapped['Tournament'] = relationship(back_populates="competitor_associations")
    competitor: Mapped['Competitor'] = relationship(back_populates="tournament_associations")
