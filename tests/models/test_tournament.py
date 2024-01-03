from datetime import datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from matamata.models import Tournament
from matamata.models.constants import TOURNAMENT_LABEL_CONSTRAINT, TOURNAMENT_START_ATTRS_CONSTRAINT
from matamata.models.exceptions import CannotUpdateTournamentDataAfterStartError


def test_create_and_retrieve_tournament(session):
    before_new_tournament = datetime.now()
    new_tournament = Tournament(
        label='2022 FIFA World Cup',
    )
    session.add(new_tournament)
    session.commit()

    tournament = session.scalar(
        select(Tournament)
        .where(
            Tournament.label == '2022 FIFA World Cup',
        )
    )

    assert tournament.label == '2022 FIFA World Cup'
    assert tournament.created > before_new_tournament
    assert tournament.updated > tournament.created
    assert tournament.matchesCreation is None
    assert tournament.numberCompetitors is None
    assert tournament.startingRound is None


def test_cannot_create_tournament_with_empty_label(session):
    empty_label_tournament = Tournament(
        label='',  # empty
    )
    session.add(empty_label_tournament)
    with pytest.raises(
        IntegrityError,
        match=TOURNAMENT_LABEL_CONSTRAINT,
    ):
        session.commit()


def test_cannot_create_tournament_with_whitespace_only_label(session):
    whitespace_label_tournament = Tournament(
        label='  ',  # whitespaces
    )
    session.add(whitespace_label_tournament)
    with pytest.raises(
        IntegrityError,
        match=TOURNAMENT_LABEL_CONSTRAINT,
    ):
        session.commit()


def test_can_create_duplicate_tournament(session):
    first_tournament = Tournament(
        label='2022 FIFA World Cup',
    )
    session.add(first_tournament)
    session.commit()
    session.refresh(first_tournament)

    second_tournament = Tournament(
        label='2022 FIFA World Cup',
    )
    session.add(second_tournament)
    session.commit()
    session.refresh(second_tournament)

    count = session.scalar(
        select(func.count('*'))
        .select_from(Tournament)
        .where(
            Tournament.label == '2022 FIFA World Cup',
        )
    )

    assert count == 2


def test_tournament_matchescreation_must_be_non_null_with_positive_numbercompetitors(session):
    tournament = Tournament(
        label='2022 FIFA World Cup',
    )
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # set matchesCreation but not numberCompetitors >= 1 nor startingRound >= 0
    tournament.matchesCreation = datetime(year=2022, month=1, day=1)
    session.add(tournament)
    with pytest.raises(
        IntegrityError,
        match=TOURNAMENT_START_ATTRS_CONSTRAINT,
    ):
        session.commit()
    session.rollback()
    session.refresh(tournament)

    # set matchesCreation and numberCompetitors >= 1 but not startingRound >= 0
    tournament.matchesCreation = datetime(year=2022, month=1, day=1)
    tournament.numberCompetitors = 1
    session.add(tournament)
    with pytest.raises(
        IntegrityError,
        match=TOURNAMENT_START_ATTRS_CONSTRAINT,
    ):
        session.commit()
    session.rollback()
    session.refresh(tournament)

    # set matchesCreation, numberCompetitors >= 1 and startingRound >= 0
    tournament.matchesCreation = datetime(year=2022, month=1, day=1)
    tournament.numberCompetitors = 1
    tournament.startingRound = 0
    session.add(tournament)
    session.commit()
    session.refresh(tournament)


def test_tournament_does_not_allow_changing_attrs_after_start(session):
    tournament = Tournament(
        label='2022 FIFA World Cup',
    )
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # set matchesCreation, numberCompetitors >= 1 and startingRound >= 0
    tournament.matchesCreation = datetime(year=2022, month=1, day=1)
    tournament.numberCompetitors = 1
    tournament.startingRound = 0
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # try to update matchesCreation after setting it
    tournament.matchesCreation = datetime(year=2021, month=1, day=1)
    session.add(tournament)
    with pytest.raises(
        CannotUpdateTournamentDataAfterStartError,
        match='matchesCreation is not allowed to be updated after Tournament start',
    ):
        session.commit()
    session.rollback()
    session.refresh(tournament)

    # try to update numberCompetitors after setting it
    tournament.numberCompetitors = 2
    session.add(tournament)
    with pytest.raises(
        CannotUpdateTournamentDataAfterStartError,
        match='numberCompetitors is not allowed to be updated after Tournament start',
    ):
        session.commit()
    session.rollback()
    session.refresh(tournament)

    # try to update startingRound after setting it
    tournament.startingRound = 1
    session.add(tournament)
    with pytest.raises(
        CannotUpdateTournamentDataAfterStartError,
        match='startingRound is not allowed to be updated after Tournament start',
    ):
        session.commit()
    session.rollback()
    session.refresh(tournament)
