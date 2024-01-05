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


START_TOURNAMENT_URL_TEMPLATE = BASE_URL + '/{tournament_uuid}/start'


def test_201_for_start_tournament_for_one_competitor(session, client, tournament, competitor):
    tournament.competitors.append(competitor)
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    response = client.post(
        START_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    response_json = response.json()

    # as UUID is dynamically generated, we will extract it for the assertion
    matches_uuid = [
        match_data['uuid']
        for match_data in response_json['matches']
    ]

    assert response.status_code == 201
    assert response.json() == {
        'tournament': {
            'uuid': str(tournament.uuid),
            'label': tournament.label,
            'startingRound': 0,
            'numberCompetitors': 1,
        },
        'competitors': [
            {
                'uuid': str(competitor.uuid),
                'label': competitor.label,
            },
        ],
        'matches': [
            {
                'uuid': matches_uuid[0],
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
            },
        ],
    }


def test_201_for_start_tournament_for_five_competitors(
    session, client, tournament, competitor1, competitor2, competitor3, competitor4, competitor5,
):
    for competitor_ in [competitor1, competitor2, competitor3, competitor4, competitor5]:
        tournament.competitors.append(competitor_)
        session.add(tournament)
    session.commit()
    session.refresh(tournament)

    response = client.post(
        START_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    response_json = response.json()

    # as UUID is dynamically generated, we will extract it for the assertion
    matches_uuid = [
        match_data['uuid']
        for match_data in response_json['matches']
    ]

    # as the competitors are randomly chosen, we will collect them to do the assertion
    competitor_dict = {
        'r2p0cA': response_json['matches'][0]['competitorA'],
        'r2p0cB': response_json['matches'][0]['competitorB'],
        'r2p1cA': response_json['matches'][1]['competitorA'],
        'r2p2cA': response_json['matches'][2]['competitorA'],
        'r2p3cA': response_json['matches'][3]['competitorA'],
    }

    assert response.status_code == 201
    assert response.json() == {
        'tournament': {
            'uuid': str(tournament.uuid),
            'label': tournament.label,
            'startingRound': 2,
            'numberCompetitors': 5,
        },
        'competitors': [
            {
                'uuid': str(competitor1.uuid),
                'label': competitor1.label,
            },
            {
                'uuid': str(competitor2.uuid),
                'label': competitor2.label,
            },
            {
                'uuid': str(competitor3.uuid),
                'label': competitor3.label,
            },
            {
                'uuid': str(competitor4.uuid),
                'label': competitor4.label,
            },
            {
                'uuid': str(competitor5.uuid),
                'label': competitor5.label,
            },
        ],
        'matches': [
            {
                'uuid': matches_uuid[0],
                'round': 2,
                'position': 0,
                'competitorA': competitor_dict['r2p0cA'],
                'competitorB': competitor_dict['r2p0cB'],
                'winner': None,
                'loser': None,
            },
            {
                'uuid': matches_uuid[1],
                'round': 2,
                'position': 1,
                'competitorA': competitor_dict['r2p1cA'],
                'competitorB': None,
                'winner': competitor_dict['r2p1cA'],
                'loser': None,
            },
            {
                'uuid': matches_uuid[2],
                'round': 2,
                'position': 2,
                'competitorA': competitor_dict['r2p2cA'],
                'competitorB': None,
                'winner': competitor_dict['r2p2cA'],
                'loser': None,
            },
            {
                'uuid': matches_uuid[3],
                'round': 2,
                'position': 3,
                'competitorA': competitor_dict['r2p3cA'],
                'competitorB': None,
                'winner': competitor_dict['r2p3cA'],
                'loser': None,
            },
            {
                'uuid': matches_uuid[4],
                'round': 1,
                'position': 0,
                'competitorA': None,
                'competitorB': competitor_dict['r2p1cA'],
                'winner': None,
                'loser': None,
            },
            {
                'uuid': matches_uuid[5],
                'round': 1,
                'position': 1,
                'competitorA': competitor_dict['r2p2cA'],
                'competitorB': competitor_dict['r2p3cA'],
                'winner': None,
                'loser': None,
            },
            {
                'uuid': matches_uuid[6],
                'round': 0,
                'position': 0,
                'competitorA': None,
                'competitorB': None,
                'winner': None,
                'loser': None,
            },
            {
                'uuid': matches_uuid[7],
                'round': 0,
                'position': 1,
                'competitorA': None,
                'competitorB': None,
                'winner': None,
                'loser': None,
            },
        ],
    }


def test_404_for_missing_tournament_during_start_tournament(client):
    response = client.post(
        START_TOURNAMENT_URL_TEMPLATE.format(
            tournament_uuid='01234567-89ab-cdef-0123-456789abcdef',
        ),
    )

    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Target Tournament does not exist',
    }


def test_409_for_started_tournament_during_start_tournament(client, session, tournament, competitor):
    # Already started tournament
    tournament.matchesCreation = datetime(year=2024, month=1, day=1)
    tournament.numberCompetitors = 1
    tournament.startingRound = 0
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    response = client.post(
        START_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    assert response.status_code == 409
    assert response.json() == {
        'detail': 'Target Tournament has already created its matches',
    }


def test_422_for_missing_competitor_during_start_tournament(client, tournament):
    response = client.post(
        START_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    assert response.status_code == 422
    assert response.json() == {
        'detail': 'Target Tournament does not have one Competitor registered yet',
    }


LIST_TOURNAMENT_MATCHES_URL_TEMPLATE = BASE_URL + '/{tournament_uuid}/match'


def test_200_for_list_tournament_matches_for_one_competitor(session, client, tournament, competitor):
    tournament.competitors.append(competitor)
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # First we start the tournament
    client.post(
        START_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    # Then we retrieve the matches
    response = client.get(
        LIST_TOURNAMENT_MATCHES_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    response_json = response.json()

    # as UUID is dynamically generated, we will extract it for the assertion
    past_matches_uuid = [
        match_data['uuid']
        for match_data in response_json['past']
    ]

    assert response.status_code == 200
    assert len(response_json['past']) == 1
    assert len(response_json['upcoming']) == 0
    assert response.json() == {
        'tournament': {
            'uuid': str(tournament.uuid),
            'label': tournament.label,
            'startingRound': 0,
            'numberCompetitors': 1,
        },
        'past': [
            {
                'uuid': past_matches_uuid[0],
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
            },
        ],
        'upcoming': [],
    }


def test_200_list_tournament_matches_for_five_competitors(
    session, client, tournament, competitor1, competitor2, competitor3, competitor4, competitor5,
):
    for competitor_ in [competitor1, competitor2, competitor3, competitor4, competitor5]:
        tournament.competitors.append(competitor_)
        session.add(tournament)
    session.commit()
    session.refresh(tournament)

    # First we start the tournament
    client.post(
        START_TOURNAMENT_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    # Then we retrieve the matches
    response = client.get(
        LIST_TOURNAMENT_MATCHES_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    response_json = response.json()

    # as UUID is dynamically generated, we will extract it for the assertion
    past_matches_uuid = [
        match_data['uuid']
        for match_data in response_json['past']
    ]
    upcoming_matches_uuid = [
        match_data['uuid']
        for match_data in response_json['upcoming']
    ]

    # as the competitors are randomly chosen, we will collect them to do the assertion
    competitor_dict = {
        'r2p0cA': response_json['upcoming'][0]['competitorA'],
        'r2p0cB': response_json['upcoming'][0]['competitorB'],
        'r2p1cA': response_json['past'][0]['competitorA'],
        'r2p2cA': response_json['past'][1]['competitorA'],
        'r2p3cA': response_json['past'][2]['competitorA'],
    }

    assert response.status_code == 200
    assert len(response_json['past']) == 3
    assert len(response_json['upcoming']) == 5
    assert response.json() == {
        'tournament': {
            'uuid': str(tournament.uuid),
            'label': tournament.label,
            'startingRound': 2,
            'numberCompetitors': 5,
        },
        'past': [
            {
                'uuid': past_matches_uuid[0],
                'round': 2,
                'position': 1,
                'competitorA': competitor_dict['r2p1cA'],
                'competitorB': None,
                'winner': competitor_dict['r2p1cA'],
                'loser': None,
            },
            {
                'uuid': past_matches_uuid[1],
                'round': 2,
                'position': 2,
                'competitorA': competitor_dict['r2p2cA'],
                'competitorB': None,
                'winner': competitor_dict['r2p2cA'],
                'loser': None,
            },
            {
                'uuid': past_matches_uuid[2],
                'round': 2,
                'position': 3,
                'competitorA': competitor_dict['r2p3cA'],
                'competitorB': None,
                'winner': competitor_dict['r2p3cA'],
                'loser': None,
            },
        ],
        'upcoming': [
            {
                'uuid': upcoming_matches_uuid[0],
                'round': 2,
                'position': 0,
                'competitorA': competitor_dict['r2p0cA'],
                'competitorB': competitor_dict['r2p0cB'],
                'winner': None,
                'loser': None,
            },
            {
                'uuid': upcoming_matches_uuid[1],
                'round': 1,
                'position': 0,
                'competitorA': None,
                'competitorB': competitor_dict['r2p1cA'],
                'winner': None,
                'loser': None,
            },
            {
                'uuid': upcoming_matches_uuid[2],
                'round': 1,
                'position': 1,
                'competitorA': competitor_dict['r2p2cA'],
                'competitorB': competitor_dict['r2p3cA'],
                'winner': None,
                'loser': None,
            },
            {
                'uuid': upcoming_matches_uuid[3],
                'round': 0,
                'position': 0,
                'competitorA': None,
                'competitorB': None,
                'winner': None,
                'loser': None,
            },
            {
                'uuid': upcoming_matches_uuid[4],
                'round': 0,
                'position': 1,
                'competitorA': None,
                'competitorB': None,
                'winner': None,
                'loser': None,
            },
        ],
    }


def test_404_for_missing_tournament_during_list_tournament_matches(client):
    response = client.get(
        LIST_TOURNAMENT_MATCHES_URL_TEMPLATE.format(
            tournament_uuid='01234567-89ab-cdef-0123-456789abcdef',
        ),
    )

    assert response.status_code == 404
    assert response.json() == {
        'detail': 'Target Tournament does not exist',
    }


def test_422_for_missing_competitor_during_list_tournament_matches(session, client, tournament, competitor):
    tournament.competitors.append(competitor)
    session.add(tournament)
    session.commit()
    session.refresh(tournament)

    response = client.get(
        LIST_TOURNAMENT_MATCHES_URL_TEMPLATE.format(tournament_uuid=tournament.uuid),
    )

    assert response.status_code == 422
    assert response.json() == {
        'detail': 'Target Tournament has not created its matches yet',
    }
