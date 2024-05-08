import uuid

import pytest

from tests.workflows.utils import create_base_workflow, faker


@pytest.fixture(scope="function")
def base_workflow(client, token):
    data = create_base_workflow(client, token)
    yield data
    client.delete(f"/workflows/{data['id']}", headers={"Authorization": f"Bearer {token}"})


def test_delete_workflow_invalid_token(client, base_workflow):
    response = client.delete(f"/workflows/{base_workflow['id']}", headers={"Authorization": "Bearer token"})
    assert response.status_code == 401


def test_delete_workflow_invalid_token_scheme(client, token, base_workflow):
    response = client.delete(f"/workflows/{base_workflow['id']}", headers={"Authorization": "Basic token"})
    assert response.status_code == 403


def test_delete_workflow_wo_auth(client, token, base_workflow):
    response = client.delete(f"/workflows/{base_workflow['id']}")
    assert response.status_code == 403


def test_delete_workflow(client, token, base_workflow):
    response = client.delete(f"/workflows/{base_workflow['id']}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 204
    assert not response.text


def test_delete_workflow_invalid_pk(client, token):
    response = client.delete(f"/workflows/{faker.random_number()}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


def test_delete_workflow_not_found(client, token):
    response = client.delete(f"/workflows/{uuid.uuid4()}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 404
    assert response.json() == {"detail": "Workflow not found"}
