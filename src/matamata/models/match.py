from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import generic_repr

from .base import IdUuidTimestampedBase
from .constants import (
    MATCH_NON_NULL_COMPETITORS_CANNOT_BE_THE_SAME,
    MATCH_POSITION_CONSTRAINT,
    MATCH_RESULT_REGISTRATION_MIGHT_REGISTER_A_LOSER,
    MATCH_RESULT_REGISTRATION_MUST_REGISTER_A_WINNER,
    MATCH_ROUND_CONSTRAINT,
    MATCH_ROUND_POSITION_CONSTRAINT,
    MATCH_TOURNAMENT_ROUND_POSITION_UNIQUE_CONSTRAINT,
)
from .tournament import Tournament


@generic_repr
class Match(IdUuidTimestampedBase):
    __tablename__ = "match"
    __table_args__ = (
        UniqueConstraint(
            "tournament_id",
            "round",
            "position",
            name=MATCH_TOURNAMENT_ROUND_POSITION_UNIQUE_CONSTRAINT,
        ),
        CheckConstraint(
            "round >= 0",
            name=MATCH_ROUND_CONSTRAINT,
        ),
        CheckConstraint(
            "position >= 0",
            name=MATCH_POSITION_CONSTRAINT,
        ),
        CheckConstraint(
            "("
            " round = 0"
            " AND position < 2"
            ") OR ("
            " round > 0"
            " AND position < pow(2, round)"
            ")",
            name=MATCH_ROUND_POSITION_CONSTRAINT,
        ),
        CheckConstraint(
            "("
            " competitor_a_id IS NULL"
            " AND competitor_b_id IS NULL"
            ") OR ("
            " competitor_a_id <> competitor_b_id"
            ")",
            name=MATCH_NON_NULL_COMPETITORS_CANNOT_BE_THE_SAME,
        ),
        CheckConstraint(
            "("
            " result_registration IS NULL"
            " AND winner_id is NULL"
            ") OR ("
            " result_registration IS NOT NULL"
            " AND winner_id IS NOT NULL"
            ")",
            name=MATCH_RESULT_REGISTRATION_MUST_REGISTER_A_WINNER,
        ),
        CheckConstraint(
            "("
            " result_registration IS NULL"
            " AND loser_id is NULL"
            ") OR ("
            " result_registration IS NOT NULL"
            " AND loser_id is NULL"
            ") OR ("
            " result_registration IS NOT NULL"
            " AND loser_id IS NOT NULL"
            ")",
            name=MATCH_RESULT_REGISTRATION_MIGHT_REGISTER_A_LOSER,
        ),
    )

    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournament.id"))
    tournament: Mapped[Tournament] = relationship(
        foreign_keys="Match.tournament_id", back_populates="matches"
    )
    round: Mapped[int] = mapped_column()
    position: Mapped[int] = mapped_column()

    competitor_a_id: Mapped[int | None] = mapped_column(ForeignKey("competitor.id"))
    competitor_b_id: Mapped[int | None] = mapped_column(ForeignKey("competitor.id"))
    competitor_a: Mapped[Optional["Competitor"]] = relationship(  # noqa: F821
        foreign_keys="Match.competitor_a_id"
    )
    competitor_b: Mapped[Optional["Competitor"]] = relationship(  # noqa: F821
        foreign_keys="Match.competitor_b_id"
    )

    result_registration: Mapped[datetime | None] = mapped_column()

    winner_id: Mapped[int | None] = mapped_column(ForeignKey("competitor.id"))
    loser_id: Mapped[int | None] = mapped_column(ForeignKey("competitor.id"))
    winner: Mapped[Optional["Competitor"]] = relationship(  # noqa: F821
        foreign_keys="Match.winner_id"
    )
    loser: Mapped[Optional["Competitor"]] = relationship(  # noqa: F821
        foreign_keys="Match.loser_id"
    )
