from datetime import datetime
from uuid import UUID

from sqlalchemy import Update, select, update
from sqlalchemy.orm import Session

from .exceptions import (
    MatchAlreadyRegisteredResult,
    MatchMissingCompetitorFromPreviousMatch,
    MatchShouldHaveAutomaticWinner,
    MatchTargetCompetitorIsNotMatchCompetitor,
)
from matamata.models import Competitor, Match, TournamentCompetitor


def store_competitor_data(
    *,
    competitor: Competitor | None,
    competitor_uuid_set: set[UUID],
    map_uuid_to_competitor: dict[UUID, Competitor],
) -> UUID | None:
    if not competitor:
        return

    competitor_uuid = competitor.uuid
    competitor_uuid_set.add(competitor_uuid)
    map_uuid_to_competitor[competitor_uuid] = competitor

    return competitor_uuid


def validate_match_to_register_result(
    *,
    match_with_tournament_and_competitors: Match,
    winner_uuid: UUID,
    session: Session,
) -> tuple[Competitor, Competitor]:
    is_starting_round = (
        match_with_tournament_and_competitors.round
        ==
        match_with_tournament_and_competitors.tournament.starting_round
    )

    competitor_uuid_set: set[UUID] = set()
    map_uuid_to_competitor: dict[UUID, Competitor] = {}

    competitor_a_uuid = store_competitor_data(
        competitor=match_with_tournament_and_competitors.competitor_a,
        competitor_uuid_set=competitor_uuid_set,
        map_uuid_to_competitor=map_uuid_to_competitor,
    )
    competitor_b_uuid = store_competitor_data(
        competitor=match_with_tournament_and_competitors.competitor_b,
        competitor_uuid_set=competitor_uuid_set,
        map_uuid_to_competitor=map_uuid_to_competitor,
    )

    has_both_competitors = competitor_a_uuid and competitor_b_uuid

    if not has_both_competitors:
        if is_starting_round:
            raise MatchShouldHaveAutomaticWinner()
        else:
            raise MatchMissingCompetitorFromPreviousMatch()

    if winner_uuid not in competitor_uuid_set:
        raise MatchTargetCompetitorIsNotMatchCompetitor()

    competitor_uuid_set.remove(winner_uuid)
    loser_uuid = competitor_uuid_set.pop()
    winner = map_uuid_to_competitor[winner_uuid]
    loser = map_uuid_to_competitor[loser_uuid]

    match_with_tournament_and_competitors.winner = winner
    match_with_tournament_and_competitors.loser = loser
    match_with_tournament_and_competitors.result_registration = datetime.utcnow()
    session.add(match_with_tournament_and_competitors)

    return winner, loser


def get_tournament_id_and_competitor_key(
    match_with_tournament_and_competitors: Match,
) -> tuple[int, str]:
    tournament_id = match_with_tournament_and_competitors.tournament_id

    if match_with_tournament_and_competitors.position % 2 == 0:
        competitor_key = 'competitor_a_id'
    else:
        competitor_key = 'competitor_b_id'

    return tournament_id, competitor_key


def update_winner_next_match_data(
    *,
    match_with_tournament_and_competitors: Match,
    winner: Competitor,
    session: Session,
):
    tournament_id, competitor_key = get_tournament_id_and_competitor_key(
        match_with_tournament_and_competitors,
    )

    update_winner_next_match_competitor = None

    if match_with_tournament_and_competitors.round > 0:
        winner_next_match_parameters = {
            "round": match_with_tournament_and_competitors.round - 1,
            "position": match_with_tournament_and_competitors.position // 2,
        }

        winner_next_match_subquery = (
            select(Match.id)
            .where(
                Match.tournament_id == tournament_id,
                Match.round == winner_next_match_parameters['round'],
                Match.position == winner_next_match_parameters['position'],
            )
            .scalar_subquery()
        )

        update_winner_tournamentcompetitor_next_match = (
            update(TournamentCompetitor)
            .where(
                TournamentCompetitor.tournament_id == tournament_id,
                TournamentCompetitor.competitor_id == winner.id,
            )
            .values(
                next_match_id=winner_next_match_subquery,
            )
        )

        update_winner_next_match_competitor = (
            update(Match)
            .where(
                Match.id == winner_next_match_subquery,
            )
            .values(
                **{
                    competitor_key: winner.id,
                }
            )
        )
    else:
        update_winner_tournamentcompetitor_next_match = (
            update(TournamentCompetitor)
            .where(
                TournamentCompetitor.tournament_id == tournament_id,
                TournamentCompetitor.competitor_id == winner.id,
            )
            .values(
                next_match_id=None,
            )
        )

    session.execute(update_winner_tournamentcompetitor_next_match)

    if update_winner_next_match_competitor is not None:
        session.execute(update_winner_next_match_competitor)


def adjust_third_place_match_for_loser(
    *,
    match_with_tournament_and_competitors: Match,
    loser: Competitor,
    tournament_id: int,
    competitor_key: str,
) -> tuple[Update, Update | None]:
    # Adjustments for third place match:
    # the only match when a loser competes in a next match
    loser_next_match_parameters = {
        "round": 0,
        "position": 1,
    }

    # There is a very specific corner case
    # when the loser of the current match is
    # the third place of a three competitor tournament.
    # This means the loser is an automatic winner of the next match
    is_third_place_out_of_three_competitors = (
        match_with_tournament_and_competitors.tournament.number_competitors == 3
    )

    loser_next_match_subquery = (
        select(Match.id)
        .where(
            Match.tournament_id == tournament_id,
            Match.round == loser_next_match_parameters['round'],
            Match.position == loser_next_match_parameters['position'],
        )
        .scalar_subquery()
    )

    additional_parameters = {}
    next_match_id_value = loser_next_match_subquery
    if is_third_place_out_of_three_competitors:
        # There is a very specific corner case
        # when the loser of the current match is
        # the third place of a three competitor tournament.
        # This means the loser won't have a next match and
        # it is an automatic winner of the next match
        next_match_id_value = None
        additional_parameters = {
            'winner_id': loser.id,
            'result_registration': datetime.utcnow(),
        }

    update_loser_tournamentcompetitor_next_match = (
        update(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == tournament_id,
            TournamentCompetitor.competitor_id == loser.id,
        )
        .values(
            next_match_id=next_match_id_value,
        )
    )

    update_loser_next_match_competitor = (
        update(Match)
        .where(
            Match.id == loser_next_match_subquery,
        )
        .values(
            **(
                {
                    competitor_key: loser.id,
                } | additional_parameters
            )
        )
    )

    return (
        update_loser_tournamentcompetitor_next_match,
        update_loser_next_match_competitor,
    )


def update_loser_next_match_data(
    *,
    match_with_tournament_and_competitors: Match,
    loser: Competitor,
    session: Session,
):
    tournament_id, competitor_key = get_tournament_id_and_competitor_key(
        match_with_tournament_and_competitors,
    )

    # On most cases, there won't be a next match for a loser
    update_loser_tournamentcompetitor_next_match = (
        update(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == tournament_id,
            TournamentCompetitor.competitor_id == loser.id,
        )
        .values(
            next_match_id=None,
        )
    )
    update_loser_next_match_competitor = None

    # There will be a next match if the current match was a semifinal one
    will_compete_third_place_match = (
        match_with_tournament_and_competitors.round == 1
    )

    if will_compete_third_place_match:
        (
            update_loser_tournamentcompetitor_next_match,
            update_loser_next_match_competitor,
        ) = adjust_third_place_match_for_loser(
            match_with_tournament_and_competitors=match_with_tournament_and_competitors,
            loser=loser,
            tournament_id=tournament_id,
            competitor_key=competitor_key,
        )

    session.execute(update_loser_tournamentcompetitor_next_match)
    if update_loser_next_match_competitor is not None:
        session.execute(update_loser_next_match_competitor)


def adjust_next_matches(
    *,
    match_with_tournament_and_competitors: Match,
    winner: Competitor,
    loser: Competitor,
    session: Session,
):
    update_winner_next_match_data(
        match_with_tournament_and_competitors=match_with_tournament_and_competitors,
        winner=winner,
        session=session,
    )

    update_loser_next_match_data(
        match_with_tournament_and_competitors=match_with_tournament_and_competitors,
        loser=loser,
        session=session,
    )


def register_match_result(
    *,
    match_with_tournament_and_competitors: Match,
    winner_uuid: UUID,
    session: Session,
):
    if match_with_tournament_and_competitors.result_registration:
        raise MatchAlreadyRegisteredResult()

    winner, loser = validate_match_to_register_result(
        match_with_tournament_and_competitors=match_with_tournament_and_competitors,
        winner_uuid=winner_uuid,
        session=session,
    )

    adjust_next_matches(
        match_with_tournament_and_competitors=match_with_tournament_and_competitors,
        winner=winner,
        loser=loser,
        session=session,
    )

    session.commit()
    session.refresh(match_with_tournament_and_competitors)

    return match_with_tournament_and_competitors
