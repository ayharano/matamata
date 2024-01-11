from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from matamata.models import Match, Tournament, TournamentCompetitor
from matamata.services import (
    register_match_result as register_match_result_service,
    start_tournament as start_tournament_service,
)


def retrieve_tournament_competitor(
    *,
    tournament_id: int,
    competitor_id: int,
    session: Session,
) -> TournamentCompetitor:
    tournament_competitor = session.scalar(
        select(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == tournament_id,
            TournamentCompetitor.competitor_id == competitor_id,
        )
    )

    return tournament_competitor


def retrieve_match_with_competitors_by_tournament_round_position(
    *,
    tournament_id: int,
    round_: int,
    position: int,
    session: Session,
) -> Match:
    match = session.scalar(
        select(Match)
        .where(
            Match.tournament_id == tournament_id,
            Match.round == round_,
            Match.position == position,
        )
        .options(
            joinedload(Match.competitor_a),
            joinedload(Match.competitor_b),
        )
    )

    return match


def retrieve_match_with_tournament_and_competitors(
    *,
    match_uuid: UUID,
    session: Session,
) -> Match:
    match = session.scalar(
        select(Match)
        .where(Match.uuid == match_uuid)
        .options(
            joinedload(Match.tournament),
            joinedload(Match.competitor_a),
            joinedload(Match.competitor_b),
        )
    )

    return match


def retrieve_tournament_with_competitors(
    *,
    tournament_uuid: UUID,
    session: Session,
) -> Tournament:
    tournament = session.scalar(
        select(Tournament)
        .where(Tournament.uuid == tournament_uuid)
        .options(
            joinedload(Tournament.competitor_associations)
            .subqueryload(TournamentCompetitor.competitor)
        )
    )

    return tournament


def start_tournament_util(
    tournament_uuid: UUID,
    session: Session,
) -> tuple[Tournament, list[Match]]:
    tournament = retrieve_tournament_with_competitors(
        tournament_uuid=tournament_uuid,
        session=session,
    )

    matches = start_tournament_service(
        tournament=tournament,
        competitor_associations=tournament.competitor_associations,
        session=session,
    )

    return tournament, matches


def register_match_result_util(
    *,
    match_uuid: UUID,
    winner_uuid: UUID,
    session: Session,
):
    match = retrieve_match_with_tournament_and_competitors(
        match_uuid=match_uuid,
        session=session,
    )

    match = register_match_result_service(
        match_with_tournament_and_competitors=match,
        winner_uuid=winner_uuid,
        session=session,
    )

    return match
