from fastapi.testclient import TestClient
import pytest

from app import create_app


@pytest.fixture(scope="session")
def application():
    return create_app()

@pytest.fixture(scope="session")
def client(application):
    client = TestClient(application)
    return client
