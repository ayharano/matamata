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
