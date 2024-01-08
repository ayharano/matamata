BASE_URL = '/competitor'


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
                'label': str(competitor.label),
            }
            for competitor in [competitor1, competitor2, competitor3, competitor4, competitor5]
        ],
    }

    response = client.get(
        BASE_URL,
    )

    assert response.status_code == 200
    assert response.json() == expected_data
