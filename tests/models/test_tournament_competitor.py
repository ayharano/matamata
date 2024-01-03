from datetime import datetime

import pytest
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from matamata.models import TournamentCompetitor


def test_create_and_retrieve_tournamentcompetitor(session, competitor, tournament):
    before_new_tournament_competitor = datetime.now()
    new_tournament_competitor = TournamentCompetitor(
        tournament=tournament,
        competitor=competitor,
    )
    session.add(new_tournament_competitor)
    session.commit()

    tournament_competitor = session.scalar(
        select(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament == tournament,
        )
    )

    assert tournament_competitor.tournament == tournament
    assert tournament_competitor.competitor == competitor
    assert tournament_competitor.created > before_new_tournament_competitor
    assert tournament_competitor.updated > competitor.created


def test_cannot_create_duplicate_tournament_competitor(session, competitor, tournament):
    first_tournament_competitor = TournamentCompetitor(
        tournament=tournament,
        competitor=competitor,
    )
    session.add(first_tournament_competitor)
    session.commit()
    session.refresh(first_tournament_competitor)

    duplicate_tournament_competitor = TournamentCompetitor(
        tournament=tournament,
        competitor=competitor,
    )
    session.add(duplicate_tournament_competitor)
    with pytest.raises(
        IntegrityError,
        match="UNIQUE constraint",
    ):
        session.commit()


def test_tournament_can_access_competitors(session, tournament, competitor1, competitor2):
    tournament.competitors.append(competitor1)
    tournament.competitors.append(competitor2)
    session.commit()
    session.refresh(tournament)

    count = session.scalar(
        select(func.count('*'))
        .select_from(TournamentCompetitor)
        .where(
            TournamentCompetitor.tournament == tournament,
        )
    )

    assert count == 2
    assert len(tournament.competitors) == 2
    assert tournament.competitors == [competitor1, competitor2]


def test_competitor_can_access_tournaments(session, competitor, tournament1, tournament2):
    competitor.tournaments.append(tournament1)
    competitor.tournaments.append(tournament2)
    session.commit()
    session.refresh(competitor)

    count = session.scalar(
        select(func.count('*'))
        .select_from(TournamentCompetitor)
        .where(
            TournamentCompetitor.competitor == competitor,
        )
    )

    assert count == 2
    assert len(competitor.tournaments) == 2
    assert competitor.tournaments == [tournament1, tournament2]
