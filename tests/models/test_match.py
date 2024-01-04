from datetime import datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from matamata.models import Match
from matamata.models.constants import (
    MATCH_ROUND_CONSTRAINT,
    MATCH_POSITION_CONSTRAINT,
    MATCH_ROUND_POSITION_CONSTRAINT,
    MATCH_NON_NULL_COMPETITORS_CANNOT_BE_THE_SAME,
    MATCH_RESULT_REGISTRATION_MUST_REGISTER_A_WINNER,
)


def test_create_and_retrieve_match(session, tournament, competitor1, competitor2):
    before_new_match = datetime.now()
    new_match = Match(
        tournament_id=tournament.id,
        round=0,
        position=0,
        competitorA_id=competitor1.id,
        competitorB_id=competitor2.id,
    )
    session.add(new_match)
    session.commit()

    match = session.scalar(
        select(Match)
        .where(
            Match.tournament == tournament,
            Match.round == 0,
            Match.position == 0,
        )
    )

    assert match.created > before_new_match
    assert match.updated > match.created
    assert match.tournament == tournament
    assert match.round == 0
    assert match.position == 0
    assert match.competitorA == competitor1
    assert match.competitorB == competitor2
    assert match.resultRegistration is None
    assert match.winner is None
    assert match.loser is None


def test_cannot_create_duplicate_match(session, tournament, competitor1, competitor2):
    first_match = Match(
        tournament_id=tournament.id,
        round=0,
        position=0,
        competitorA_id=competitor1.id,
        competitorB_id=competitor2.id,
    )
    session.add(first_match)
    session.commit()
    session.refresh(first_match)

    duplicate_match = Match(
        tournament_id=tournament.id,
        round=0,
        position=0,
        competitorA_id=competitor1.id,
        competitorB_id=competitor2.id,
    )
    session.add(duplicate_match)
    with pytest.raises(
        IntegrityError,
        match="UNIQUE constraint",
    ):
        session.commit()


def test_match_round_must_be_non_negative(session, tournament, competitor1, competitor2):
    match = Match(
        tournament_id=tournament.id,
        round=-1,
        position=0,
        competitorA_id=competitor1.id,
        competitorB_id=competitor2.id,
    )
    session.add(match)

    with pytest.raises(
        IntegrityError,
        match=MATCH_ROUND_CONSTRAINT,
    ):
        session.commit()


def test_match_position_must_be_non_negative(session, tournament, competitor1, competitor2):
    match = Match(
        tournament_id=tournament.id,
        round=0,
        position=-1,
        competitorA_id=competitor1.id,
        competitorB_id=competitor2.id,
    )
    session.add(match)

    with pytest.raises(
        IntegrityError,
        match=MATCH_POSITION_CONSTRAINT,
    ):
        session.commit()


def test_match_position_cannot_be_greater_or_equal_round_power_2(session, tournament, competitor1, competitor2):
    match = Match(
        tournament_id=tournament.id,
        round=1,
        position=2,
        competitorA_id=competitor1.id,
        competitorB_id=competitor2.id,
    )
    session.add(match)

    with pytest.raises(
        IntegrityError,
        match=MATCH_ROUND_POSITION_CONSTRAINT,
    ):
        session.commit()


def test_match_competitors_cannot_be_the_same(session, tournament, competitor):
    match = Match(
        tournament_id=tournament.id,
        round=1,
        position=1,
        competitorA_id=competitor.id,
        competitorB_id=competitor.id,
    )
    session.add(match)

    with pytest.raises(
        IntegrityError,
        match=MATCH_NON_NULL_COMPETITORS_CANNOT_BE_THE_SAME,
    ):
        session.commit()


def test_match_winner_must_register_resultregistration(session, tournament, competitor):
    match = Match(
        tournament_id=tournament.id,
        round=1,
        position=1,
        competitorA_id=competitor.id,
        competitorB_id=None,
        winner_id=competitor.id,
    )
    session.add(match)

    with pytest.raises(
        IntegrityError,
        match=MATCH_RESULT_REGISTRATION_MUST_REGISTER_A_WINNER,
    ):
        session.commit()


def test_match_resultregistration_must_register_winner(session, tournament, competitor):
    match = Match(
        tournament_id=tournament.id,
        round=1,
        position=1,
        competitorA_id=competitor.id,
        competitorB_id=None,
        resultRegistration=datetime(year=2024, month=1, day=1),
        winner_id=None,
    )
    session.add(match)

    with pytest.raises(
        IntegrityError,
        match=MATCH_RESULT_REGISTRATION_MUST_REGISTER_A_WINNER,
    ):
        session.commit()


def test_tournament_can_access_matches(session, tournament, competitor, competitor1, competitor2):
    final_match = Match(
        tournament_id=tournament.id,
        round=0,
        position=0,
        competitorA_id=competitor1.id,
        competitorB_id=competitor2.id,
    )
    third_place_match = Match(
        tournament_id=tournament.id,
        round=0,
        position=1,
        competitorA_id=competitor.id,
        competitorB_id=None,
    )
    session.add_all([final_match, third_place_match])
    session.commit()

    assert tournament.matches == [final_match, third_place_match]
