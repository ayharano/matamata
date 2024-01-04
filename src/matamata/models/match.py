from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import generic_repr

from .base import IdUuidTimestampedBase
from .constants import (
    MATCH_ROUND_CONSTRAINT,
    MATCH_POSITION_CONSTRAINT,
    MATCH_ROUND_POSITION_CONSTRAINT,
    MATCH_TOURNAMENT_ROUND_POSITION_UNIQUE_CONSTRAINT,
    MATCH_NON_NULL_COMPETITORS_CANNOT_BE_THE_SAME,
    MATCH_RESULT_REGISTRATION_MUST_REGISTER_A_WINNER,
    MATCH_RESULT_REGISTRATION_MIGHT_REGISTER_A_LOSER,
)
from .tournament import Tournament


@generic_repr
class Match(IdUuidTimestampedBase):
    __tablename__ = 'match'
    __table_args__ = (
        UniqueConstraint(
            'tournament_id',
            'round',
            'position',
            name=MATCH_TOURNAMENT_ROUND_POSITION_UNIQUE_CONSTRAINT,
        ),
        CheckConstraint(
            'round >= 0',
            name=MATCH_ROUND_CONSTRAINT,
        ),
        CheckConstraint(
            'position >= 0',
            name=MATCH_POSITION_CONSTRAINT,
        ),
        CheckConstraint(
            '('
            ' round == 0'
            ' AND position < 2'
            ') OR ('
            ' round > 0'
            ' AND position < pow(2, round)'
            ')',
            name=MATCH_ROUND_POSITION_CONSTRAINT,
        ),
        CheckConstraint(
            '('
            ' competitorA_id IS NULL'
            ' AND competitorB_id IS NULL'
            ') OR ('
            ' competitorA_id <> competitorB_id'
            ')',
            name=MATCH_NON_NULL_COMPETITORS_CANNOT_BE_THE_SAME,
        ),
        CheckConstraint(
            '('
            ' resultRegistration IS NULL'
            ' AND winner_id is NULL'
            ') OR ('
            ' resultRegistration IS NOT NULL'
            ' AND winner_id IS NOT NULL'
            ')',
            name=MATCH_RESULT_REGISTRATION_MUST_REGISTER_A_WINNER,
        ),
        CheckConstraint(
            '('
            ' resultRegistration IS NULL'
            ' AND loser_id is NULL'
            ') OR ('
            ' resultRegistration IS NOT NULL'
            ' AND loser_id is NULL'
            ') OR ('
            ' resultRegistration IS NOT NULL'
            ' AND loser_id IS NOT NULL'
            ')',
            name=MATCH_RESULT_REGISTRATION_MIGHT_REGISTER_A_LOSER,
        ),
    )

    tournament_id: Mapped[int] = mapped_column(ForeignKey('tournament.id'))
    tournament: Mapped[Tournament] = relationship(foreign_keys='Match.tournament_id', back_populates='matches')
    round: Mapped[int] = mapped_column()
    position: Mapped[int] = mapped_column()

    competitorA_id: Mapped[int | None] = mapped_column(ForeignKey('competitor.id'))
    competitorB_id: Mapped[int | None] = mapped_column(ForeignKey('competitor.id'))
    competitorA: Mapped[Optional['Competitor']] = relationship(foreign_keys='Match.competitorA_id')
    competitorB: Mapped[Optional['Competitor']] = relationship(foreign_keys='Match.competitorB_id')

    resultRegistration: Mapped[datetime | None] = mapped_column()

    winner_id: Mapped[int | None] = mapped_column(ForeignKey('competitor.id'))
    loser_id: Mapped[int | None] = mapped_column(ForeignKey('competitor.id'))
    winner: Mapped[Optional['Competitor']] = relationship(foreign_keys='Match.winner_id')
    loser: Mapped[Optional['Competitor']] = relationship(foreign_keys='Match.loser_id')
