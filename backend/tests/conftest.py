import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool

from app.db import Base
from app.main import create_app


@pytest.fixture
def client():
    url = os.getenv("TEST_DATABASE_URL", "sqlite://")
    assert "test" in url or url == "sqlite://", "Use an isolated test database"
    kwargs = (
        {"poolclass": StaticPool, "connect_args": {"check_same_thread": False}}
        if url == "sqlite://"
        else {}
    )
    engine = create_engine(url, **kwargs)
    if url == "sqlite://":

        @event.listens_for(engine, "connect")
        def unicode_lower(connection, _record):
            connection.create_function(
                "lower", 1, lambda text: text.lower() if text is not None else None
            )

    Base.metadata.create_all(engine)
    app = create_app(engine=engine, secret="test-only-secret-" * 4, origin="http://testserver")
    with TestClient(app) as session:
        yield session
    Base.metadata.drop_all(engine)
    engine.dispose()


def register(client, email="volunteer@example.com", role="VOLUNTEER"):
    return client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123!",
            "name": "Анна",
            "role": role,
            "organization_name": "Добрые дела" if role == "ORGANIZER" else None,
        },
        headers={"Origin": "http://testserver"},
    )


def login(client, email="volunteer@example.com"):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "StrongPassword123!"},
        headers={"Origin": "http://testserver"},
    )
    assert response.status_code == 200, response.text
    return {"Origin": "http://testserver", "X-CSRF-Token": response.json()["csrf_token"]}
