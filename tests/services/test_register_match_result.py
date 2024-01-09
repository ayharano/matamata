from datetime import datetime

import pytest

from matamata.models import Match
from matamata.services import register_match_result
from matamata.services.exceptions import (
    MatchAlreadyRegisteredResult,
    MatchMissingCompetitorFromPreviousMatch,
    MatchShouldHaveAutomaticWinner,
    MatchTargetCompetitorIsNotMatchCompetitor,
)
from tests.utils import (
    retrieve_match_with_tournament_and_competitors,
    retrieve_tournament_competitor,
    start_tournament_util,
)


def test_register_match_result_for_final_match(
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
    assert final.competitorA_id is not None
    assert final.competitorB_id is not None
    assert final.winner_id is None
    assert final.loser_id is None

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = retrieve_tournament_competitor(
        tournament_id=final.tournament_id,
        competitor_id=final.competitorA_id,
        session=session,
    )
    tournament_competitor_competitorB = retrieve_tournament_competitor(
        tournament_id=final.tournament_id,
        competitor_id=final.competitorB_id,
        session=session,
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
    tournament, matches = start_tournament_util(
        tournament_uuid=tournament.uuid,
        session=session,
    )

    assert len(matches) == 4
    semifinal_r1p0 = matches[0]

    assert semifinal_r1p0.round == 1
    assert semifinal_r1p0.position == 0
    assert semifinal_r1p0.competitorA_id is not None
    assert semifinal_r1p0.competitorB_id is not None
    assert semifinal_r1p0.winner_id is None
    assert semifinal_r1p0.loser_id is None

    final_match = matches[2]
    third_place_match = matches[3]

    assert final_match.round == 0
    assert final_match.position == 0
    assert third_place_match.round == 0
    assert third_place_match.position == 1

    assert final_match.competitorA_id is None
    assert final_match.competitorB_id is not None
    assert third_place_match.competitorA_id is None
    assert third_place_match.competitorB_id is None

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = retrieve_tournament_competitor(
        tournament_id=semifinal_r1p0.tournament_id,
        competitor_id=semifinal_r1p0.competitorA_id,
        session=session,
    )
    tournament_competitor_competitorB = retrieve_tournament_competitor(
        tournament_id=semifinal_r1p0.tournament_id,
        competitor_id=semifinal_r1p0.competitorB_id,
        session=session,
    )

    assert tournament_competitor_competitorA.next_match_id == semifinal_r1p0.id
    assert tournament_competitor_competitorB.next_match_id == semifinal_r1p0.id

    match = retrieve_match_with_tournament_and_competitors(
        match_uuid=semifinal_r1p0.uuid,
        session=session,
    )
    match = register_match_result(
        match_with_tournament_and_competitors=match,
        winner_uuid=semifinal_r1p0.competitorB.uuid,
        session=session,
    )

    assert match.winner_id == match.competitorB_id
    assert match.loser_id == match.competitorA_id

    # Validate changes related to next match after registering match result
    session.refresh(semifinal_r1p0)
    session.refresh(final_match)
    session.refresh(third_place_match)
    session.refresh(tournament_competitor_competitorA)
    session.refresh(tournament_competitor_competitorB)

    assert final_match.competitorA_id == semifinal_r1p0.winner_id
    assert third_place_match.competitorA_id == semifinal_r1p0.loser_id
    assert third_place_match.winner_id == semifinal_r1p0.loser_id
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
    tournament, matches = start_tournament_util(
        tournament_uuid=tournament.uuid,
        session=session,
    )

    assert len(matches) == 8
    semifinal_r1p1 = matches[5]

    assert semifinal_r1p1.round == 1
    assert semifinal_r1p1.position == 1
    assert semifinal_r1p1.competitorA_id is not None
    assert semifinal_r1p1.competitorB_id is not None
    assert semifinal_r1p1.winner_id is None
    assert semifinal_r1p1.loser_id is None

    final_match = matches[6]
    third_place_match = matches[7]

    assert final_match.round == 0
    assert final_match.position == 0
    assert third_place_match.round == 0
    assert third_place_match.position == 1

    assert final_match.competitorB_id is None
    assert third_place_match.competitorB_id is None

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = retrieve_tournament_competitor(
        tournament_id=semifinal_r1p1.tournament_id,
        competitor_id=semifinal_r1p1.competitorA_id,
        session=session,
    )
    tournament_competitor_competitorB = retrieve_tournament_competitor(
        tournament_id=semifinal_r1p1.tournament_id,
        competitor_id=semifinal_r1p1.competitorB_id,
        session=session,
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
    tournament, matches = start_tournament_util(
        tournament_uuid=tournament.uuid,
        session=session,
    )

    assert len(matches) == 8
    entry_match = matches[0]

    assert entry_match.round == 2
    assert entry_match.position == 0
    assert entry_match.competitorA_id is not None
    assert entry_match.competitorB_id is not None
    assert entry_match.winner_id is None
    assert entry_match.loser_id is None

    next_match = matches[4]

    assert next_match.round == 1
    assert next_match.position == 0

    assert next_match.competitorA_id is None

    # Verify next match for entry_match.competitorA and entry_match.competitorB
    tournament_competitor_competitorA = retrieve_tournament_competitor(
        tournament_id=entry_match.tournament_id,
        competitor_id=entry_match.competitorA_id,
        session=session,
    )
    tournament_competitor_competitorB = retrieve_tournament_competitor(
        tournament_id=entry_match.tournament_id,
        competitor_id=entry_match.competitorB_id,
        session=session,
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
