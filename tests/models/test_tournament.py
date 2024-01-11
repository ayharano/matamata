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


def test_tournament_matches_creation_must_be_non_null_with_positive_number_competitors(session):
    tournament = Tournament(
        label='2022 FIFA World Cup',
    )
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # set matches_creation but not number_competitors >= 1 nor starting_round >= 0
    tournament.matches_creation = datetime(year=2022, month=1, day=1)
    session.add(tournament)
    with pytest.raises(
        IntegrityError,
        match=TOURNAMENT_START_ATTRS_CONSTRAINT,
    ):
        session.commit()
    session.rollback()
    session.refresh(tournament)

    # set matches_creation and number_competitors >= 1 but not starting_round >= 0
    tournament.matches_creation = datetime(year=2022, month=1, day=1)
    tournament.number_competitors = 1
    session.add(tournament)
    with pytest.raises(
        IntegrityError,
        match=TOURNAMENT_START_ATTRS_CONSTRAINT,
    ):
        session.commit()
    session.rollback()
    session.refresh(tournament)

    # set matches_creation, number_competitors >= 1 and starting_round >= 0
    tournament.matches_creation = datetime(year=2022, month=1, day=1)
    tournament.number_competitors = 1
    tournament.starting_round = 0
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

    # set matches_creation, number_competitors >= 1 and starting_round >= 0
    tournament.matches_creation = datetime(year=2022, month=1, day=1)
    tournament.number_competitors = 1
    tournament.starting_round = 0
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # try to update matches_creation after setting it
    tournament.matches_creation = datetime(year=2021, month=1, day=1)
    session.add(tournament)
    with pytest.raises(
        CannotUpdateTournamentDataAfterStartError,
        match='matches_creation is not allowed to be updated after Tournament start',
    ):
        session.commit()
    session.rollback()
    session.refresh(tournament)

    # try to update number_competitors after setting it
    tournament.number_competitors = 2
    session.add(tournament)
    with pytest.raises(
        CannotUpdateTournamentDataAfterStartError,
        match='number_competitors is not allowed to be updated after Tournament start',
    ):
        session.commit()
    session.rollback()
    session.refresh(tournament)

    # try to update starting_round after setting it
    tournament.starting_round = 1
    session.add(tournament)
    with pytest.raises(
        CannotUpdateTournamentDataAfterStartError,
        match='starting_round is not allowed to be updated after Tournament start',
    ):
        session.commit()
    session.rollback()
    session.refresh(tournament)
