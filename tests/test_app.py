def test_api_docs_endpoint_is_accessible(client):
    response = client.get("/docs")
    assert response.status_code == 200


def test_api_docs_definition_is_accessible(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
