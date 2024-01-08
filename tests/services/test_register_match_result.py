from datetime import datetime
from uuid import UUID

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from matamata.models import Match, TournamentCompetitor
from matamata.services import register_match_result
from matamata.services.exceptions import (
    MatchAlreadyRegisteredResult,
    MatchMissingCompetitorFromPreviousMatch,
    MatchShouldHaveAutomaticWinner,
    MatchTargetCompetitorIsNotMatchCompetitor,
)
from tests.routers.test_tournament import START_TOURNAMENT_URL_TEMPLATE


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
            joinedload(Match.competitorA),
            joinedload(Match.competitorB),
        )
    )

    return match


def test_register_match_result_for_final_match(
    session, client, tournament, competitor1, competitor2,
):
    for competitor_ in [competitor1, competitor2]:
        tournament.competitors.append(competitor_)
        session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # First we start the tournament
    response_start = client.post(
        START_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    response_start_json = response_start.json()

    assert len(response_start_json['matches']) == 1
    json_final = response_start_json['matches'][0]

    assert json_final['round'] == 0
    assert json_final['position'] == 0
    assert json_final['competitorA'] is not None
    assert json_final['competitorB'] is not None
    assert json_final['winner'] is None
    assert json_final['loser'] is None

    final = session.scalar(
        select(Match)
        .where(
            Match.tournament_id == tournament.id,
            Match.round == 0,
            Match.position == 0,
        )
        .options(
            joinedload(Match.competitorA),
            joinedload(Match.competitorB),
        )
    )

    assert str(final.competitorA.uuid) == json_final['competitorA']['uuid']
    assert str(final.competitorB.uuid) == json_final['competitorB']['uuid']

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = session.scalar(
        select(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == final.tournament_id,
            TournamentCompetitor.competitor_id == final.competitorA_id,
        )
    )
    tournament_competitor_competitorB = session.scalar(
        select(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == final.tournament_id,
            TournamentCompetitor.competitor_id == final.competitorB_id,
        )
    )

    assert tournament_competitor_competitorA.next_match_id == final.id
    assert tournament_competitor_competitorB.next_match_id == final.id

    match = retrieve_match_with_tournament_and_competitors(
        match_uuid=final.uuid,
        session=session,
    )
    match = register_match_result(
        match_with_tournament_and_competitors=match,
        winner_uuid=final.competitorB.uuid,
        session=session,
    )

    assert match.winner_id == match.competitorB_id
    assert match.loser_id == match.competitorA_id

    # Validate changes related to next match after registering match result
    session.refresh(tournament_competitor_competitorA)
    session.refresh(tournament_competitor_competitorB)

    assert tournament_competitor_competitorA.next_match_id is None
    assert tournament_competitor_competitorB.next_match_id is None


def test_200_for_register_match_result_for_semifinal_match_for_three_competitors(
    session, client, tournament, competitor1, competitor2, competitor3,
):
    for competitor_ in [competitor1, competitor2, competitor3]:
        tournament.competitors.append(competitor_)
        session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # First we start the tournament
    response_start = client.post(
        START_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    response_start_json = response_start.json()

    assert len(response_start_json['matches']) == 4
    json_semifinal = response_start_json['matches'][0]

    assert json_semifinal['round'] == 1
    assert json_semifinal['position'] == 0
    assert json_semifinal['competitorA'] is not None
    assert json_semifinal['competitorB'] is not None
    assert json_semifinal['winner'] is None
    assert json_semifinal['loser'] is None

    semifinal = session.scalar(
        select(Match)
        .where(
            Match.tournament_id == tournament.id,
            Match.round == 1,
            Match.position == 0,
        )
        .options(
            joinedload(Match.competitorA),
            joinedload(Match.competitorB),
        )
    )
    final_match, third_place_match = session.scalars(
        select(Match)
        .where(
            Match.tournament_id == tournament.id,
            Match.round == 0,
        )
        .order_by(
            Match.position.asc(),
        )
    ).all()

    assert final_match.competitorA_id is None
    assert final_match.competitorB_id is not None
    assert third_place_match.competitorA_id is None
    assert third_place_match.competitorB_id is None

    assert str(semifinal.competitorA.uuid) == json_semifinal['competitorA']['uuid']
    assert str(semifinal.competitorB.uuid) == json_semifinal['competitorB']['uuid']

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = session.scalar(
        select(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == semifinal.tournament_id,
            TournamentCompetitor.competitor_id == semifinal.competitorA_id,
        )
    )
    tournament_competitor_competitorB = session.scalar(
        select(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == semifinal.tournament_id,
            TournamentCompetitor.competitor_id == semifinal.competitorB_id,
        )
    )

    assert tournament_competitor_competitorA.next_match_id == semifinal.id
    assert tournament_competitor_competitorB.next_match_id == semifinal.id

    match = retrieve_match_with_tournament_and_competitors(
        match_uuid=semifinal.uuid,
        session=session,
    )
    match = register_match_result(
        match_with_tournament_and_competitors=match,
        winner_uuid=semifinal.competitorB.uuid,
        session=session,
    )

    assert match.winner_id == match.competitorB_id
    assert match.loser_id == match.competitorA_id

    # Validate changes related to next match after registering match result
    session.refresh(semifinal)
    session.refresh(final_match)
    session.refresh(third_place_match)
    session.refresh(tournament_competitor_competitorA)
    session.refresh(tournament_competitor_competitorB)

    assert final_match.competitorA_id == semifinal.winner_id
    assert third_place_match.competitorA_id == semifinal.loser_id
    assert third_place_match.winner_id == semifinal.loser_id
    assert tournament_competitor_competitorA.next_match_id is None
    assert tournament_competitor_competitorB.next_match_id == final_match.id


def test_register_match_result_for_round_1_match(
    session, client, tournament, competitor1, competitor2, competitor3, competitor4, competitor5,
):
    for competitor_ in [competitor1, competitor2, competitor3, competitor4, competitor5]:
        tournament.competitors.append(competitor_)
        session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # First we start the tournament
    response_start = client.post(
        START_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    response_start_json = response_start.json()

    json_semifinal_r1p1 = response_start_json['matches'][5]

    assert json_semifinal_r1p1['round'] == 1
    assert json_semifinal_r1p1['position'] == 1
    assert json_semifinal_r1p1['competitorA'] is not None
    assert json_semifinal_r1p1['competitorB'] is not None
    assert json_semifinal_r1p1['winner'] is None
    assert json_semifinal_r1p1['loser'] is None

    semifinal_r1p1 = session.scalar(
        select(Match)
        .where(
            Match.tournament_id == tournament.id,
            Match.round == 1,
            Match.position == 1,
        )
        .options(
            joinedload(Match.competitorA),
            joinedload(Match.competitorB),
        )
    )

    assert str(semifinal_r1p1.competitorA.uuid) == json_semifinal_r1p1['competitorA']['uuid']
    assert str(semifinal_r1p1.competitorB.uuid) == json_semifinal_r1p1['competitorB']['uuid']

    final_match, third_place_match = session.scalars(
        select(Match)
        .where(
            Match.tournament_id == tournament.id,
            Match.round == 0,
        )
        .order_by(
            Match.round.desc(),
            Match.position.asc(),
        )
    ).all()

    assert final_match.competitorB_id is None
    assert third_place_match.competitorB_id is None

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = session.scalar(
        select(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == semifinal_r1p1.tournament_id,
            TournamentCompetitor.competitor_id == semifinal_r1p1.competitorA_id,
        )
    )
    tournament_competitor_competitorB = session.scalar(
        select(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == semifinal_r1p1.tournament_id,
            TournamentCompetitor.competitor_id == semifinal_r1p1.competitorB_id,
        )
    )

    assert tournament_competitor_competitorA.next_match_id == semifinal_r1p1.id
    assert tournament_competitor_competitorB.next_match_id == semifinal_r1p1.id

    match = retrieve_match_with_tournament_and_competitors(
        match_uuid=semifinal_r1p1.uuid,
        session=session,
    )
    match = register_match_result(
        match_with_tournament_and_competitors=match,
        winner_uuid=semifinal_r1p1.competitorA.uuid,
        session=session,
    )

    assert match.winner_id == match.competitorA_id
    assert match.loser_id == match.competitorB_id

    # Validate changes related to next match after registering match result
    session.refresh(semifinal_r1p1)
    session.refresh(final_match)
    session.refresh(third_place_match)
    session.refresh(tournament_competitor_competitorA)
    session.refresh(tournament_competitor_competitorB)

    assert final_match.competitorB_id == semifinal_r1p1.winner_id
    assert tournament_competitor_competitorA.next_match_id == final_match.id
    assert tournament_competitor_competitorB.next_match_id == third_place_match.id


def test_register_match_result_for_round_greater_than_1_entry_match(
    session, client, tournament, competitor1, competitor2, competitor3, competitor4, competitor5,
):
    for competitor_ in [competitor1, competitor2, competitor3, competitor4, competitor5]:
        tournament.competitors.append(competitor_)
        session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # First we start the tournament
    response_start = client.post(
        START_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    response_start_json = response_start.json()

    json_entry_match = response_start_json['matches'][0]

    assert json_entry_match['round'] == 2
    assert json_entry_match['position'] == 0
    assert json_entry_match['winner'] is None
    assert json_entry_match['loser'] is None

    entry_match = session.scalar(
        select(Match)
        .where(
            Match.tournament_id == tournament.id,
            Match.round == 2,
            Match.position == 0,
        )
        .options(
            joinedload(Match.competitorA),
            joinedload(Match.competitorB),
        )
    )

    assert str(entry_match.competitorA.uuid) == json_entry_match['competitorA']['uuid']
    assert str(entry_match.competitorB.uuid) == json_entry_match['competitorB']['uuid']

    next_match = session.scalar(
        select(Match)
        .where(
            Match.tournament_id == tournament.id,
            Match.round == 1,
            Match.position == 0,
        )
    )

    assert next_match.competitorA_id is None

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = session.scalar(
        select(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == entry_match.tournament_id,
            TournamentCompetitor.competitor_id == entry_match.competitorA_id,
        )
    )
    tournament_competitor_competitorB = session.scalar(
        select(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament_id == entry_match.tournament_id,
            TournamentCompetitor.competitor_id == entry_match.competitorB_id,
        )
    )

    assert tournament_competitor_competitorA.next_match_id == entry_match.id
    assert tournament_competitor_competitorB.next_match_id == entry_match.id

    match = retrieve_match_with_tournament_and_competitors(
        match_uuid=entry_match.uuid,
        session=session,
    )
    match = register_match_result(
        match_with_tournament_and_competitors=match,
        winner_uuid=entry_match.competitorA.uuid,
        session=session,
    )

    assert match.winner_id == match.competitorA_id
    assert match.loser_id == match.competitorB_id

    # Validate changes related to next match after registering match result
    session.refresh(entry_match)
    session.refresh(next_match)
    session.refresh(tournament_competitor_competitorA)
    session.refresh(tournament_competitor_competitorB)

    assert next_match.competitorA_id == entry_match.winner_id
    assert tournament_competitor_competitorA.next_match_id == next_match.id
    assert tournament_competitor_competitorB.next_match_id is None


def test_match_with_registered_result_during_register_match_result(client, session, tournament, competitor):
    tournament.matchesCreation = datetime(year=2024, month=1, day=1)
    tournament.numberCompetitors = 1
    tournament.startingRound = 0
    tournament.competitors.append(competitor)
    session.add(tournament)
    final_match = Match(
        tournament_id=tournament.id,
        round=0,
        position=0,
        competitorA_id=competitor.id,
        resultRegistration=datetime(year=2024, month=1, day=2),
        winner_id=competitor.id,
    )
    session.add(final_match)
    session.commit()
    session.refresh(final_match)

    match = retrieve_match_with_tournament_and_competitors(
        match_uuid=final_match.uuid,
        session=session,
    )

    with pytest.raises(MatchAlreadyRegisteredResult):
        register_match_result(
            match_with_tournament_and_competitors=match,
            winner_uuid=competitor.uuid,
            session=session,
        )


def test_match_that_should_have_automatic_winner_during_register_match_result(client, session, tournament, competitor):
    tournament.matchesCreation = datetime(year=2024, month=1, day=1)
    tournament.numberCompetitors = 1
    tournament.startingRound = 0
    tournament.competitors.append(competitor)
    session.add(tournament)
    final_match = Match(
        tournament_id=tournament.id,
        round=0,
        position=0,
        competitorA_id=competitor.id,
    )
    session.add(final_match)
    session.commit()
    session.refresh(final_match)

    match = retrieve_match_with_tournament_and_competitors(
        match_uuid=final_match.uuid,
        session=session,
    )

    with pytest.raises(MatchShouldHaveAutomaticWinner):
        register_match_result(
            match_with_tournament_and_competitors=match,
            winner_uuid=competitor.uuid,
            session=session,
        )


def test_missing_competitor_during_register_match_result(client, session, tournament, competitor1, competitor2, competitor3):
    tournament.matchesCreation = datetime(year=2024, month=1, day=1)
    tournament.numberCompetitors = 3
    tournament.startingRound = 1
    for competitor_ in [competitor1, competitor2, competitor3]:
        tournament.competitors.append(competitor_)
    session.add(tournament)
    final_match = Match(
        tournament_id=tournament.id,
        round=0,
        position=0,
    )
    session.add(final_match)
    session.commit()
    session.refresh(final_match)

    match = retrieve_match_with_tournament_and_competitors(
        match_uuid=final_match.uuid,
        session=session,
    )

    with pytest.raises(MatchMissingCompetitorFromPreviousMatch):
        register_match_result(
            match_with_tournament_and_competitors=match,
            winner_uuid=competitor3.uuid,
            session=session,
        )


def test_competitor_not_match_competitor_during_register_match_result(client, session, tournament, competitor1, competitor2, competitor3):
    tournament.matchesCreation = datetime(year=2024, month=1, day=1)
    tournament.numberCompetitors = 3
    tournament.startingRound = 1
    for competitor_ in [competitor1, competitor2, competitor3]:
        tournament.competitors.append(competitor_)
    session.add(tournament)
    final_match = Match(
        tournament_id=tournament.id,
        round=0,
        position=0,
        competitorA_id=competitor1.id,
        competitorB_id=competitor2.id,
    )
    session.add(final_match)
    session.commit()
    session.refresh(final_match)

    match = retrieve_match_with_tournament_and_competitors(
        match_uuid=final_match.uuid,
        session=session,
    )

    with pytest.raises(MatchTargetCompetitorIsNotMatchCompetitor):
        register_match_result(
            match_with_tournament_and_competitors=match,
            winner_uuid=competitor3.uuid,
            session=session,
        )
