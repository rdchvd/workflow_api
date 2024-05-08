from tests.utils import compare_results
from tests.workflows.utils import faker, get_workflow_data


def test_create_workflow_invalid_token(client):
    response = client.post("/workflows/", json=get_workflow_data(), headers={"Authorization": "Bearer token"})
    assert response.status_code == 401


def test_create_workflow_invalid_token_scheme(client, token):
    response = client.post("/workflows/", json=get_workflow_data(), headers={"Authorization": "Basic token"})
    assert response.status_code == 403


def test_create_workflow_wo_auth(client, token):
    response = client.post(
        "/workflows/",
        json=get_workflow_data(),
    )
    assert response.status_code == 403


def test_create_workflow_full(client, token):
    test_data = get_workflow_data()
    response = client.post("/workflows/", json=test_data, headers={"Authorization": f"Bearer {token}"})
    data = response.json()

    assert response.status_code == 201
    compare_results(test_data, data)
    assert "id" in data


def test_create_workflow_wo_optional(client, token):
    test_data = get_workflow_data()
    test_data.pop("description")

    response = client.post("/workflows/", json=test_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201

    data = response.json()
    compare_results(test_data, data)
    assert "id" in data


def test_create_workflow_w_incorrect_types(client, token):
    test_data = {"name": faker.random_number(), "description": faker.boolean()}

    response = client.post("/workflows/", json=test_data, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422

    data = response.json()
    assert "name" in data["detail"][0]["loc"]
    assert "description" in data["detail"][1]["loc"]
