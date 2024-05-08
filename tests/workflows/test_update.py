import uuid

import pytest

from tests.utils import compare_results
from tests.workflows.utils import create_base_workflow, faker, get_workflow_data


@pytest.fixture(scope="function")
def base_workflow(client, token):
    data = create_base_workflow(client, token)
    yield data
    client.delete(f"/workflows/{data['id']}", headers={"Authorization": f"Bearer {token}"})


def test_update_workflow_invalid_token(client, base_workflow):
    response = client.patch(
        f"/workflows/{base_workflow['id']}", json=get_workflow_data(), headers={"Authorization": "Bearer token"}
    )
    assert response.status_code == 401


def test_update_workflow_invalid_token_scheme(client, token, base_workflow):
    response = client.patch(
        f"/workflows/{base_workflow['id']}", json=get_workflow_data(), headers={"Authorization": "Basic token"}
    )
    assert response.status_code == 403


def test_update_workflow_wo_auth(client, token, base_workflow):
    response = client.patch(
        f"/workflows/{base_workflow['id']}",
        json=get_workflow_data(),
    )
    assert response.status_code == 403


def test_update_workflow_full(client, token, base_workflow):
    test_data = get_workflow_data()
    response = client.patch(
        f"/workflows/{base_workflow['id']}", json=test_data, headers={"Authorization": f"Bearer {token}"}
    )
    data = response.json()

    assert response.status_code == 200
    compare_results(test_data, data)


def test_update_workflow_partial(client, token, base_workflow):
    test_data = get_workflow_data()
    test_data.pop("description")

    response = client.patch(
        f"/workflows/{base_workflow['id']}", json=test_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200

    data = response.json()
    compare_results(test_data, data)
    assert data["description"] == base_workflow["description"]


def test_update_workflow_w_incorrect_types(client, token, base_workflow):
    test_data = {"name": faker.random_number(), "description": faker.boolean()}

    response = client.patch(
        f"/workflows/{base_workflow['id']}", json=test_data, headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422

    data = response.json()
    assert "name" in data["detail"][0]["loc"]
    assert "description" in data["detail"][1]["loc"]


def test_update_workflow_invalid_pk(client, token):
    response = client.patch(
        f"/workflows/{faker.random_number()}", json=get_workflow_data(), headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 422


def test_update_workflow_not_found(client, token):
    response = client.patch(
        f"/workflows/{uuid.uuid4()}", json=get_workflow_data(), headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Workflow not found"}
