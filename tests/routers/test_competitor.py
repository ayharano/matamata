from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from matamata.models import Tournament, TournamentCompetitor
from matamata.services import start_tournament as start_tournament_service


BASE_URL = '/competitor'


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


def test_create_competitor(client):
    response = client.post(
        BASE_URL,
        json={
            'label': '\t\nSouth Korea\n ',
        },
    )

    response_json = response.json()

    # as UUID is dynamically generated, we will extract it for the assertion
    response_uuid = response_json['uuid']

    assert response.status_code == 201
    assert response.json() == {
        'uuid': response_uuid,
        'label': 'South Korea',
    }


def test_list_competitors(client, competitor1, competitor2, competitor3, competitor4, competitor5):
    expected_data = {
        'competitors': [
            {
                'uuid': str(competitor.uuid),
                'label': competitor.label,
            }
            for competitor in [competitor1, competitor2, competitor3, competitor4, competitor5]
        ],
    }

    response = client.get(
        BASE_URL,
    )

    assert response.status_code == 200
    assert response.json() == expected_data


GET_COMPETITOR_DETAIL_URL_TEMPLATE = BASE_URL + '/{competitor_uuid}'


def test_200_get_competitor_detail_for_competitor_in_past_ongoing_upcoming_tournaments(
        session, client, competitor1, competitor2, tournament1, tournament2, tournament3,
):
    # past
    competitor1.tournaments.append(tournament1)
    session.add(competitor1)

    # ongoing
    tournament2.competitors.append(competitor1)
    tournament2.competitors.append(competitor2)
    session.add(tournament2)

    # upcoming
    tournament3.competitors.append(competitor1)
    session.add(tournament3)

    session.commit()
    session.refresh(competitor1)
    session.refresh(tournament2)
    session.refresh(tournament3)

    # start tournament1 with one competitor
    tournament1 = retrieve_tournament_with_competitors(
        tournament_uuid=tournament1.uuid,
        session=session,
    )

    start_tournament_service(
        tournament=tournament1,
        competitor_associations=tournament1.competitor_associations,
        session=session,
    )

    # start tournament2 with two competitor2
    tournament2 = retrieve_tournament_with_competitors(
        tournament_uuid=tournament2.uuid,
        session=session,
    )

    start_tournament_service(
        tournament=tournament2,
        competitor_associations=tournament2.competitor_associations,
        session=session,
    )

    response = client.get(
        GET_COMPETITOR_DETAIL_URL_TEMPLATE.format(competitor_uuid=competitor1.uuid),
    )

    assert response.status_code == 200
    assert response.json() == {
        'competitor': {
            'uuid': str(competitor1.uuid),
            'label': competitor1.label,
        },
        'tournaments': {
            'past': [
                {
                    'uuid': str(tournament1.uuid),
                    'label': tournament1.label,
                },
            ],
            'ongoing': [
                {
                    'uuid': str(tournament2.uuid),
                    'label': tournament2.label,
                },
            ],
            'upcoming': [
                {
                    'uuid': str(tournament3.uuid),
                    'label': tournament3.label,
                },
            ],
        }
    }


def test_200_get_competitor_detail_for_competitor_in_no_tournament(client, competitor):
    response = client.get(
        GET_COMPETITOR_DETAIL_URL_TEMPLATE.format(competitor_uuid=competitor.uuid),
    )

    assert response.status_code == 200
    assert response.json() == {
        'competitor': {
            'uuid': str(competitor.uuid),
            'label': competitor.label,
        },
        'tournaments': {
            'past': [],
            'ongoing': [],
            'upcoming': [],
        }
    }


def test_200_get_competitor_detail_for_competitor_in_a_past_tournament(session, client, competitor, tournament):
    competitor.tournaments.append(tournament)
    session.add(competitor)
    session.commit()
    session.refresh(competitor)

    tournament = retrieve_tournament_with_competitors(
        tournament_uuid=tournament.uuid,
        session=session,
    )

    start_tournament_service(
        tournament=tournament,
        competitor_associations=tournament.competitor_associations,
        session=session,
    )

    response = client.get(
        GET_COMPETITOR_DETAIL_URL_TEMPLATE.format(competitor_uuid=competitor.uuid),
    )

    assert response.status_code == 200
    assert response.json() == {
        'competitor': {
            'uuid': str(competitor.uuid),
            'label': competitor.label,
        },
        'tournaments': {
            'past': [
                {
                    'uuid': str(tournament.uuid),
                    'label': tournament.label,
                },
            ],
            'ongoing': [],
            'upcoming': [],
        }
    }


def test_200_get_competitor_detail_for_competitor_in_an_ongoing_tournament(session, client, competitor1, competitor2, tournament):
    tournament.competitors.append(competitor1)
    tournament.competitors.append(competitor2)
    session.add(tournament)
    session.commit()
    session.refresh(tournament)
    session.refresh(competitor1)
    session.refresh(competitor2)

    tournament = retrieve_tournament_with_competitors(
        tournament_uuid=tournament.uuid,
        session=session,
    )

    start_tournament_service(
        tournament=tournament,
        competitor_associations=tournament.competitor_associations,
        session=session,
    )

    response = client.get(
        GET_COMPETITOR_DETAIL_URL_TEMPLATE.format(competitor_uuid=competitor2.uuid),
    )

    assert response.status_code == 200
    assert response.json() == {
        'competitor': {
            'uuid': str(competitor2.uuid),
            'label': competitor2.label,
        },
        'tournaments': {
            'past': [],
            'ongoing': [
                {
                    'uuid': str(tournament.uuid),
                    'label': tournament.label,
                },
            ],
            'upcoming': [],
        }
    }


def test_200_get_competitor_detail_for_competitor_in_an_unstarted_tournament(session, client, competitor, tournament):
    competitor.tournaments.append(tournament)
    session.add(competitor)
    session.commit()
    session.refresh(competitor)

    response = client.get(
        GET_COMPETITOR_DETAIL_URL_TEMPLATE.format(competitor_uuid=competitor.uuid),
    )

    assert response.status_code == 200
    assert response.json() == {
        'competitor': {
            'uuid': str(competitor.uuid),
            'label': competitor.label,
        },
        'tournaments': {
            'past': [],
            'ongoing': [],
            'upcoming': [
                {
                    'uuid': str(tournament.uuid),
                    'label': tournament.label,
                },
            ],
        }
    }


def test_404_for_missing_competitor_during_get_competitor_detail(client):
    response = client.get(
        GET_COMPETITOR_DETAIL_URL_TEMPLATE.format(
            competitor_uuid='01234567-89ab-cdef-0123-456789abcdef',
        )
    )

    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Target Competitor does not exist',
    }
