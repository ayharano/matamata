from datetime import datetime


BASE_URL = '/tournament'


def test_create_tournament(client):
    response = client.post(
        BASE_URL,
        json={
            'label': '\n 2002 FIFA World Cup\t\n',
        },
    )

    response_json = response.json()

    # as UUID is dynamically generated, we will extract it for the assertion
    response_uuid = response_json['uuid']

    assert response.status_code == 201
    assert response.json() == {
        'uuid': response_uuid,
        'label': '2002 FIFA World Cup',
    }


REGISTER_COMPETITOR_IN_TOURNAMENT_URL_TEMPLATE = BASE_URL + '/{tournament_uuid}/competitor'


def test_201_for_register_competitor_in_tournament(client, tournament, competitor):
    response = client.post(
        REGISTER_COMPETITOR_IN_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
        json={
            'competitor_uuid': str(competitor.uuid),
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        'tournament': {
            'uuid': str(tournament.uuid),
            'label': tournament.label,
        },
        'competitor': {
            'uuid': str(competitor.uuid),
            'label': competitor.label,
        },
    }


def test_404_for_missing_tournament_during_register_competitor_in_tournament(client, competitor):
    response = client.post(
        REGISTER_COMPETITOR_IN_TOURNAMENT_URL_TEMPLATE.format(
            tournament_uuid='01234567-89ab-cdef-0123-456789abcdef',
        ),
        json={
            'competitor_uuid': str(competitor.uuid),
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Target Tournament does not exist',
    }


def test_409_for_started_tournament_during_register_competitor_in_tournament(client, session, tournament, competitor):
    # Already started tournament
    tournament.matchesCreation = datetime(year=2024, month=1, day=1)
    tournament.numberCompetitors = 1
    tournament.startingRound = 0
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    response = client.post(
        REGISTER_COMPETITOR_IN_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
        json={
            'competitor_uuid': str(competitor.uuid),
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        'detail': 'Target Tournament has already created its matches and does not allow new Competitors registration',
    }


def test_404_for_missing_competitor_during_register_competitor_in_tournament(client, tournament):
    response = client.post(
        REGISTER_COMPETITOR_IN_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
        json={
            'competitor_uuid': '01234567-89ab-cdef-0123-456789abcdef',
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Target Competitor does not exist',
    }


def test_409_for_already_registered_competitor_during_register_competitor_in_tournament(client, session, tournament, competitor):
    tournament.competitors.append(competitor)
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    response = client.post(
        REGISTER_COMPETITOR_IN_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
        json={
            'competitor_uuid': str(competitor.uuid),
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        'detail': 'Target Competitor is already registered in target Tournament',
    }
