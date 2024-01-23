from __future__ import annotations

from sqlalchemy import CheckConstraint, String
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy_utils import generic_repr

from .base import IdUuidTimestampedBase
from .constants import COMPETITOR_LABEL_CONSTRAINT
from .tournament_competitor import TournamentCompetitor


@generic_repr
class Competitor(IdUuidTimestampedBase):
    __tablename__ = "competitor"
    __table_args__ = (
        CheckConstraint(
            "NOT(TRIM(label) LIKE '')",
            name=COMPETITOR_LABEL_CONSTRAINT,
        ),
    )

    label: Mapped[str] = mapped_column(String(255))

    tournament_associations: Mapped[list[TournamentCompetitor]] = relationship(
        cascade="all, delete-orphan",
        overlaps="competitor",
    )
    tournaments: AssociationProxy[list["Tournament"]] = association_proxy(  # noqa: F821
        "tournament_associations",
        "tournament",
        creator=lambda tournament_: TournamentCompetitor(tournament=tournament_),
    )
    next_matches: AssociationProxy[list["Match"]] = association_proxy(  # noqa: F821
        "tournament_associations",
        "next_match",
    )
