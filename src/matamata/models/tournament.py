from datetime import datetime

from sqlalchemy import CheckConstraint, String, inspect
from sqlalchemy.event import listens_for
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import generic_repr

from .base import IdUuidTimestampedBase
from .constants import TOURNAMENT_LABEL_CONSTRAINT, TOURNAMENT_START_ATTRS_CONSTRAINT
from .exceptions import CannotUpdateTournamentDataAfterStartError
from .tournament_competitor import TournamentCompetitor


SET_AFTER_START_ATTRS = {'matchesCreation', 'numberCompetitors', 'startingRound'}


@generic_repr
class Tournament(IdUuidTimestampedBase):
    __tablename__ = 'tournament'
    __table_args__ = (
        CheckConstraint(
            "NOT(TRIM(label) LIKE '')",
            name=TOURNAMENT_LABEL_CONSTRAINT,
        ),
        CheckConstraint(
            "("
            " matchesCreation IS NULL"
            " AND numberCompetitors IS NULL"
            " AND startingRound IS NULL"
            ") OR ("
            " matchesCreation IS NOT NULL"
            " AND numberCompetitors IS NOT NULL"
            " AND startingRound IS NOT NULL"
            " AND numberCompetitors >= 1"
            " AND startingRound >= 0"
            ")",
            name=TOURNAMENT_START_ATTRS_CONSTRAINT,
        ),
    )

    label: Mapped[str] = mapped_column(String(255))
    matchesCreation: Mapped[datetime | None] = mapped_column()
    numberCompetitors: Mapped[int | None] = mapped_column()
    startingRound: Mapped[int | None] = mapped_column()

    competitors: Mapped[list['Competitor']] = relationship(
        secondary=TournamentCompetitor.__table__,
        back_populates='tournaments',
    )
    competitor_associations: Mapped[list[TournamentCompetitor]] = relationship(
        back_populates='tournament',
    )

    matches: Mapped[list['Match']] = relationship(back_populates='tournament')


@listens_for(Tournament, 'before_update')
def prevent_tournament_update_after_start(mapper, connection, target):
    inspected_target = inspect(target)
    allowed_deleted_values = [[None], tuple()]

    for attribute_name in SET_AFTER_START_ATTRS:
        attribute = getattr(inspected_target.attrs, attribute_name)
        if attribute.history.deleted not in allowed_deleted_values:
            raise CannotUpdateTournamentDataAfterStartError(
                f'{attribute_name} is not allowed to be updated after Tournament start'
            )
