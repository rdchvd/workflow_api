from typing import Generator

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from core.main import app

test_user_data = {"email": "test@test.com", "password": "test"}


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    """
    Run Alembic migrations before tests start.
    """
    alembic_config = Config("alembic.ini")
    command.upgrade(alembic_config, "head")
    print("DB migrations completed.")

    yield
    command.downgrade(alembic_config, "base")
    print("Rollback DB migrations completed.")


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    """
    Overrides the normal database access with test database,
    and yields a configured test client
    """

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session", autouse=True)
async def create_user(client, setup_db):
    client.post(
        "/auth/register/",
        json=test_user_data,
    )


@pytest.fixture(scope="session")
async def token(client, create_user):
    response = client.post(
        "/auth/login/",
        json=test_user_data,
    )
    if response.is_success:
        return response.json()["access"]
    else:
        print(f"Failed to get token. Error: {response.json()}")


