from datetime import datetime

from sqlalchemy import CheckConstraint, String, inspect
from sqlalchemy.event import listens_for
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import generic_repr

from .base import IdUuidTimestampedBase
from .constants import TOURNAMENT_LABEL_CONSTRAINT, TOURNAMENT_START_ATTRS_CONSTRAINT
from .exceptions import CannotUpdateTournamentDataAfterStartError
from .tournament_competitor import TournamentCompetitor

SET_AFTER_START_ATTRS = {"matches_creation", "number_competitors", "starting_round"}


@generic_repr
class Tournament(IdUuidTimestampedBase):
    __tablename__ = "tournament"
    __table_args__ = (
        CheckConstraint(
            "NOT(TRIM(label) LIKE '')",
            name=TOURNAMENT_LABEL_CONSTRAINT,
        ),
        CheckConstraint(
            "("
            " matches_creation IS NULL"
            " AND number_competitors IS NULL"
            " AND starting_round IS NULL"
            ") OR ("
            " matches_creation IS NOT NULL"
            " AND number_competitors IS NOT NULL"
            " AND starting_round IS NOT NULL"
            " AND number_competitors >= 1"
            " AND starting_round >= 0"
            ")",
            name=TOURNAMENT_START_ATTRS_CONSTRAINT,
        ),
    )

    label: Mapped[str] = mapped_column(String(255))
    matches_creation: Mapped[datetime | None] = mapped_column()
    number_competitors: Mapped[int | None] = mapped_column()
    starting_round: Mapped[int | None] = mapped_column()

    matches: Mapped[list["Match"]] = relationship(  # noqa: F821
        back_populates="tournament"
    )

    competitor_associations: Mapped[list[TournamentCompetitor]] = relationship(
        cascade="all, delete-orphan",
        overlaps="tournament",
    )
    competitors: AssociationProxy[list["Competitor"]] = association_proxy(  # noqa: F821
        "competitor_associations",
        "competitor",
        creator=lambda competitor_: TournamentCompetitor(competitor=competitor_),
    )
    # column-targeted association proxy
    next_matches: AssociationProxy[list["Match"]] = association_proxy(  # noqa: F821
        "competitor_associations",
        "next_match",
    )


@listens_for(Tournament, "before_update")
def prevent_tournament_update_after_start(mapper, connection, target):
    inspected_target = inspect(target)
    allowed_deleted_values = [[None], tuple()]

    for attribute_name in SET_AFTER_START_ATTRS:
        attribute = getattr(inspected_target.attrs, attribute_name)
        if attribute.history.deleted not in allowed_deleted_values:
            raise CannotUpdateTournamentDataAfterStartError(
                f"{attribute_name} is not allowed to be updated after Tournament start"
            )
