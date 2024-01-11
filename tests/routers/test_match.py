from datetime import datetime

from matamata.models import Match
from tests.utils import (
    retrieve_tournament_competitor,
    start_tournament_util,
)


BASE_URL = '/match'

GET_MATCH_DETAIL_URL_TEMPLATE = BASE_URL + '/{match_uuid}'
REGISTER_MATCH_RESULT_URL_TEMPLATE = BASE_URL + '/{match_uuid}'


def test_200_for_get_match_detail_with_result_not_registered_yet(
    session, client, tournament, competitor1, competitor2,
):
    for competitor_ in [competitor1, competitor2]:
        tournament.competitors.append(competitor_)
        session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # First we start the tournament
    tournament, matches = start_tournament_util(
        tournament_uuid=tournament.uuid,
        session=session,
    )

    assert len(matches) == 1
    final = matches[0]

    assert final.round == 0
    assert final.position == 0
    assert final.competitor_a_id is not None
    assert final.competitor_b_id is not None
    assert final.winner_id is None
    assert final.loser_id is None

    response = client.get(
        GET_MATCH_DETAIL_URL_TEMPLATE.format(match_uuid=final.uuid),
    )

    assert response.status_code == 200
    assert response.json() == {
        'uuid': str(final.uuid),
        'round': 0,
        'position': 0,
        'competitorA': {
            'uuid': str(final.competitor_a.uuid),
            'label': final.competitor_a.label,
        },
        'competitorB': {
            'uuid': str(final.competitor_b.uuid),
            'label': final.competitor_b.label,
        },
        'winner': None,
        'loser': None,
        'tournament': {
            'uuid': str(tournament.uuid),
            'label': tournament.label,
            'numberCompetitors': tournament.number_competitors,
            'startingRound': tournament.starting_round,
        },
    }


def test_200_for_get_match_detail_with_result_registered_with_one_competitor_only(
    session, client, tournament, competitor,
):
    tournament.competitors.append(competitor)
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # First we start the tournament
    tournament, matches = start_tournament_util(
        tournament_uuid=tournament.uuid,
        session=session,
    )

    assert len(matches) == 1
    final = matches[0]

    assert final.round == 0
    assert final.position == 0
    assert final.competitor_a_id == competitor.id
    assert final.competitor_b_id is None
    assert final.winner_id == competitor.id
    assert final.loser_id is None

    response = client.get(
        GET_MATCH_DETAIL_URL_TEMPLATE.format(match_uuid=final.uuid),
    )

    assert response.status_code == 200
    assert response.json() == {
        'uuid': str(final.uuid),
        'round': 0,
        'position': 0,
        'competitorA': {
            'uuid': str(competitor.uuid),
            'label': competitor.label,
        },
        'competitorB': None,
        'winner': {
            'uuid': str(competitor.uuid),
            'label': competitor.label,
        },
        'loser': None,
        'tournament': {
            'uuid': str(tournament.uuid),
            'label': tournament.label,
            'numberCompetitors': tournament.number_competitors,
            'startingRound': tournament.starting_round,
        },
    }


def test_404_for_missing_match_during_get_match_detail(client, competitor):
    response = client.get(
        GET_MATCH_DETAIL_URL_TEMPLATE.format(
            match_uuid='01234567-89ab-cdef-0123-456789abcdef',
        ),
    )

    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Target Match does not exist',
    }


def test_200_for_register_match_result_for_final_match(
    session, client, tournament, competitor1, competitor2,
):
    for competitor_ in [competitor1, competitor2]:
        tournament.competitors.append(competitor_)
        session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # First we start the tournament
    tournament, matches = start_tournament_util(
        tournament_uuid=tournament.uuid,
        session=session,
    )

    assert len(matches) == 1
    final = matches[0]

    assert final.round == 0
    assert final.position == 0
    assert final.competitor_a_id is not None
    assert final.competitor_b_id is not None
    assert final.winner_id is None
    assert final.loser_id is None

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = retrieve_tournament_competitor(
        tournament_id=final.tournament_id,
        competitor_id=final.competitor_a_id,
        session=session,
    )
    tournament_competitor_competitorB = retrieve_tournament_competitor(
        tournament_id=final.tournament_id,
        competitor_id=final.competitor_b_id,
        session=session,
    )

    assert tournament_competitor_competitorA.next_match_id == final.id
    assert tournament_competitor_competitorB.next_match_id == final.id

    response = client.post(
        REGISTER_MATCH_RESULT_URL_TEMPLATE.format(match_uuid=final.uuid),
        json={
            'winner_uuid': str(final.competitor_b.uuid),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'uuid': str(final.uuid),
        'round': 0,
        'position': 0,
        'competitorA': {
            'uuid': str(final.competitor_a.uuid),
            'label': final.competitor_a.label,
        },
        'competitorB': {
            'uuid': str(final.competitor_b.uuid),
            'label': final.competitor_b.label,
        },
        'winner': {
            'uuid': str(final.competitor_b.uuid),
            'label': final.competitor_b.label,
        },
        'loser': {
            'uuid': str(final.competitor_a.uuid),
            'label': final.competitor_a.label,
        },
        'tournament': {
            'uuid': str(tournament.uuid),
            'label': tournament.label,
            'numberCompetitors': tournament.number_competitors,
            'startingRound': tournament.starting_round,
        },
    }

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
    tournament, matches = start_tournament_util(
        tournament_uuid=tournament.uuid,
        session=session,
    )

    assert len(matches) == 4
    semifinal_r1p0 = matches[0]

    assert semifinal_r1p0.round == 1
    assert semifinal_r1p0.position == 0
    assert semifinal_r1p0.competitor_a_id is not None
    assert semifinal_r1p0.competitor_b_id is not None
    assert semifinal_r1p0.winner_id is None
    assert semifinal_r1p0.loser_id is None

    final_match = matches[2]
    third_place_match = matches[3]

    assert final_match.round == 0
    assert final_match.position == 0
    assert third_place_match.round == 0
    assert third_place_match.position == 1

    assert final_match.competitor_a_id is None
    assert final_match.competitor_b_id is not None
    assert third_place_match.competitor_a_id is None
    assert third_place_match.competitor_b_id is None

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = retrieve_tournament_competitor(
        tournament_id=semifinal_r1p0.tournament_id,
        competitor_id=semifinal_r1p0.competitor_a_id,
        session=session,
    )
    tournament_competitor_competitorB = retrieve_tournament_competitor(
        tournament_id=semifinal_r1p0.tournament_id,
        competitor_id=semifinal_r1p0.competitor_b_id,
        session=session,
    )

    assert tournament_competitor_competitorA.next_match_id == semifinal_r1p0.id
    assert tournament_competitor_competitorB.next_match_id == semifinal_r1p0.id

    response = client.post(
        REGISTER_MATCH_RESULT_URL_TEMPLATE.format(match_uuid=semifinal_r1p0.uuid),
        json={
            'winner_uuid': str(semifinal_r1p0.competitor_b.uuid),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'uuid': str(semifinal_r1p0.uuid),
        'round': 1,
        'position': 0,
        'competitorA': {
            'uuid': str(semifinal_r1p0.competitor_a.uuid),
            'label': semifinal_r1p0.competitor_a.label,
        },
        'competitorB': {
            'uuid': str(semifinal_r1p0.competitor_b.uuid),
            'label': semifinal_r1p0.competitor_b.label,
        },
        'winner': {
            'uuid': str(semifinal_r1p0.competitor_b.uuid),
            'label': semifinal_r1p0.competitor_b.label,
        },
        'loser': {
            'uuid': str(semifinal_r1p0.competitor_a.uuid),
            'label': semifinal_r1p0.competitor_a.label,
        },
        'tournament': {
            'uuid': str(tournament.uuid),
            'label': tournament.label,
            'numberCompetitors': tournament.number_competitors,
            'startingRound': tournament.starting_round,
        },
    }

    # Validate changes related to next match after registering match result
    session.refresh(semifinal_r1p0)
    session.refresh(final_match)
    session.refresh(third_place_match)
    session.refresh(tournament_competitor_competitorA)
    session.refresh(tournament_competitor_competitorB)

    assert final_match.competitor_a_id == semifinal_r1p0.winner_id
    assert third_place_match.competitor_a_id == semifinal_r1p0.loser_id
    assert third_place_match.winner_id == semifinal_r1p0.loser_id
    assert tournament_competitor_competitorA.next_match_id is None
    assert tournament_competitor_competitorB.next_match_id == final_match.id


def test_200_for_register_match_result_for_round_1_match(
    session, client, tournament, competitor1, competitor2, competitor3, competitor4, competitor5,
):
    for competitor_ in [competitor1, competitor2, competitor3, competitor4, competitor5]:
        tournament.competitors.append(competitor_)
        session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # First we start the tournament
    tournament, matches = start_tournament_util(
        tournament_uuid=tournament.uuid,
        session=session,
    )

    semifinal_r1p1 = matches[5]

    assert semifinal_r1p1.round == 1
    assert semifinal_r1p1.position == 1
    assert semifinal_r1p1.competitor_a_id is not None
    assert semifinal_r1p1.competitor_b_id is not None
    assert semifinal_r1p1.winner_id is None
    assert semifinal_r1p1.loser_id is None

    final_match = matches[6]
    third_place_match = matches[7]

    assert final_match.round == 0
    assert final_match.position == 0
    assert third_place_match.round == 0
    assert third_place_match.position == 1

    assert final_match.competitor_b_id is None
    assert third_place_match.competitor_b_id is None

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = retrieve_tournament_competitor(
        tournament_id=semifinal_r1p1.tournament_id,
        competitor_id=semifinal_r1p1.competitor_a_id,
        session=session,
    )
    tournament_competitor_competitorB = retrieve_tournament_competitor(
        tournament_id=semifinal_r1p1.tournament_id,
        competitor_id=semifinal_r1p1.competitor_b_id,
        session=session,
    )

    assert tournament_competitor_competitorA.next_match_id == semifinal_r1p1.id
    assert tournament_competitor_competitorB.next_match_id == semifinal_r1p1.id

    response = client.post(
        REGISTER_MATCH_RESULT_URL_TEMPLATE.format(match_uuid=semifinal_r1p1.uuid),
        json={
            'winner_uuid': str(semifinal_r1p1.competitor_a.uuid),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'uuid': str(semifinal_r1p1.uuid),
        'round': 1,
        'position': 1,
        'competitorA': {
            'uuid': str(semifinal_r1p1.competitor_a.uuid),
            'label': semifinal_r1p1.competitor_a.label,
        },
        'competitorB': {
            'uuid': str(semifinal_r1p1.competitor_b.uuid),
            'label': semifinal_r1p1.competitor_b.label,
        },
        'winner': {
            'uuid': str(semifinal_r1p1.competitor_a.uuid),
            'label': semifinal_r1p1.competitor_a.label,
        },
        'loser': {
            'uuid': str(semifinal_r1p1.competitor_b.uuid),
            'label': semifinal_r1p1.competitor_b.label,
        },
        'tournament': {
            'uuid': str(tournament.uuid),
            'label': tournament.label,
            'numberCompetitors': tournament.number_competitors,
            'startingRound': tournament.starting_round,
        },
    }

    # Validate changes related to next match after registering match result
    session.refresh(semifinal_r1p1)
    session.refresh(final_match)
    session.refresh(third_place_match)
    session.refresh(tournament_competitor_competitorA)
    session.refresh(tournament_competitor_competitorB)

    assert final_match.competitor_b_id == semifinal_r1p1.winner_id
    assert tournament_competitor_competitorA.next_match_id == final_match.id
    assert tournament_competitor_competitorB.next_match_id == third_place_match.id


def test_200_for_register_match_result_for_round_greater_than_1_entry_match(
    session, client, tournament, competitor1, competitor2, competitor3, competitor4, competitor5,
):
    for competitor_ in [competitor1, competitor2, competitor3, competitor4, competitor5]:
        tournament.competitors.append(competitor_)
        session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # First we start the tournament
    tournament, matches = start_tournament_util(
        tournament_uuid=tournament.uuid,
        session=session,
    )

    entry_match = matches[0]

    assert entry_match.round == 2
    assert entry_match.position == 0
    assert entry_match.competitor_a_id is not None
    assert entry_match.competitor_b_id is not None
    assert entry_match.winner_id is None
    assert entry_match.loser_id is None

    next_match = matches[4]

    assert next_match.round == 1
    assert next_match.position == 0
    assert next_match.competitor_a_id is None

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = retrieve_tournament_competitor(
        tournament_id=entry_match.tournament_id,
        competitor_id=entry_match.competitor_a_id,
        session=session,
    )
    tournament_competitor_competitorB = retrieve_tournament_competitor(
        tournament_id=entry_match.tournament_id,
        competitor_id=entry_match.competitor_b_id,
        session=session,
    )

    assert tournament_competitor_competitorA.next_match_id == entry_match.id
    assert tournament_competitor_competitorB.next_match_id == entry_match.id

    response = client.post(
        REGISTER_MATCH_RESULT_URL_TEMPLATE.format(match_uuid=entry_match.uuid),
        json={
            'winner_uuid': str(entry_match.competitor_a.uuid),
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        'uuid': str(entry_match.uuid),
        'round': 2,
        'position': 0,
        'competitorA': {
            'uuid': str(entry_match.competitor_a.uuid),
            'label': entry_match.competitor_a.label,
        },
        'competitorB': {
            'uuid': str(entry_match.competitor_b.uuid),
            'label': entry_match.competitor_b.label,
        },
        'winner': {
            'uuid': str(entry_match.competitor_a.uuid),
            'label': entry_match.competitor_a.label,
        },
        'loser': {
            'uuid': str(entry_match.competitor_b.uuid),
            'label': entry_match.competitor_b.label,
        },
        'tournament': {
            'uuid': str(tournament.uuid),
            'label': tournament.label,
            'numberCompetitors': tournament.number_competitors,
            'startingRound': tournament.starting_round,
        },
    }

    # Validate changes related to next match after registering match result
    session.refresh(entry_match)
    session.refresh(next_match)
    session.refresh(tournament_competitor_competitorA)
    session.refresh(tournament_competitor_competitorB)

    assert next_match.competitor_a_id == entry_match.winner_id
    assert tournament_competitor_competitorA.next_match_id == next_match.id
    assert tournament_competitor_competitorB.next_match_id is None


def test_404_for_missing_match_during_register_match_result(client, competitor):
    response = client.post(
        REGISTER_MATCH_RESULT_URL_TEMPLATE.format(
            match_uuid='01234567-89ab-cdef-0123-456789abcdef',
        ),
        json={
            'winner_uuid': str(competitor.uuid),
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Target Match does not exist',
    }


def test_409_for_match_with_registered_result_during_register_match_result(client, session, tournament, competitor):
    tournament.matchesCreation = datetime(year=2024, month=1, day=1)
    tournament.numberCompetitors = 1
    tournament.startingRound = 0
    tournament.competitors.append(competitor)
    session.add(tournament)
    final_match = Match(
        tournament_id=tournament.id,
        round=0,
        position=0,
        competitor_a_id=competitor.id,
        result_registration=datetime(year=2024, month=1, day=2),
        winner_id=competitor.id,
    )
    session.add(final_match)
    session.commit()
    session.refresh(final_match)

    response = client.post(
        REGISTER_MATCH_RESULT_URL_TEMPLATE.format(match_uuid=final_match.uuid),
        json={
            'winner_uuid': str(competitor.uuid),
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        'detail': 'Target Match has already registered its result',
    }


def test_409_for_match_that_should_have_automatic_winner_during_register_match_result(client, session, tournament, competitor):
    tournament.matches_creation = datetime(year=2024, month=1, day=1)
    tournament.number_competitors = 1
    tournament.starting_round = 0
    tournament.competitors.append(competitor)
    session.add(tournament)
    final_match = Match(
        tournament_id=tournament.id,
        round=0,
        position=0,
        competitor_a_id=competitor.id,
    )
    session.add(final_match)
    session.commit()
    session.refresh(final_match)

    response = client.post(
        REGISTER_MATCH_RESULT_URL_TEMPLATE.format(match_uuid=final_match.uuid),
        json={
            'winner_uuid': str(competitor.uuid),
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        'detail': 'Target Match should have elected an automatic winner',
    }


def test_422_for_missing_competitor_during_register_match_result(client, session, tournament, competitor1, competitor2, competitor3):
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

    response = client.post(
        REGISTER_MATCH_RESULT_URL_TEMPLATE.format(match_uuid=final_match.uuid),
        json={
            'winner_uuid': str(competitor3.uuid),
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        'detail': (
            'Target Match is not ready to register a result due to'
            ' registered previous Matches but missing Competitor'
        )
    }


def test_409_for_competitor_not_match_competitor_during_register_match_result(client, session, tournament, competitor1, competitor2, competitor3):
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
        competitor_a_id=competitor1.id,
        competitor_b_id=competitor2.id,
    )
    session.add(final_match)
    session.commit()
    session.refresh(final_match)

    response = client.post(
        REGISTER_MATCH_RESULT_URL_TEMPLATE.format(match_uuid=final_match.uuid),
        json={
            'winner_uuid': str(competitor3.uuid),
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        'detail': 'Target Competitor is not a target Match competitor',
    }
