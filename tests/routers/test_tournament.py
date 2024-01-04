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
