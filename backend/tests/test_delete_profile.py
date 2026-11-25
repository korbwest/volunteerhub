import pytest
from conftest import login, register
from sqlalchemy.orm import Session
from test_projects import payload

from app.models import User


@pytest.mark.parametrize("role", ["VOLUNTEER", "ORGANIZER"])
def test_delete_own_profile_clears_session(client, role):
    user_id = register(client, role=role).json()["id"]
    other_id = register(client, email="other@example.com").json()["id"]
    headers = login(client)
    token = client.cookies.get("session")
    response = client.delete("/api/profile", headers=headers)
    assert response.status_code == 204
    assert response.content == b""
    assert client.cookies.get("session") is None
    assert client.get("/api/profile").status_code == 401
    with Session(client.app.state.engine) as db:
        assert db.get(User, user_id) is None
        assert db.get(User, other_id) is not None
    client.cookies.set("session", token)
    assert client.get("/api/auth/me").status_code == 401
    assert client.delete("/api/profile", headers=headers).status_code == 401
    assert (
        client.post(
            "/api/auth/login",
            json={"email": "volunteer@example.com", "password": "StrongPassword123!"},
            headers={"Origin": "http://testserver"},
        ).status_code
        == 401
    )


@pytest.mark.parametrize("status", ["DRAFT", "PUBLISHED", "ARCHIVED"])
def test_profile_with_projects_cannot_be_deleted(client, status):
    register(client, role="ORGANIZER")
    headers = login(client)
    project_id = client.post("/api/projects", json=payload(), headers=headers).json()["id"]
    if status != "DRAFT":
        assert (
            client.post(
                f"/api/projects/{project_id}/status", json={"status": status}, headers=headers
            ).status_code
            == 200
        )
    assert client.delete("/api/profile", headers=headers).status_code == 409
    assert client.get("/api/profile").status_code == 200
    assert client.get(f"/api/projects/{project_id}").status_code == 200


def test_profile_deletion_requires_session_csrf_and_origin(client):
    assert client.delete("/api/profile", headers={"Origin": "http://testserver"}).status_code == 401
    register(client)
    headers = login(client)
    assert client.delete("/api/profile", headers={"Origin": "http://testserver"}).status_code == 403
    assert (
        client.delete("/api/profile", headers={**headers, "X-CSRF-Token": "wrong"}).status_code
        == 403
    )
    assert (
        client.delete("/api/profile", headers={**headers, "Origin": "http://other"}).status_code
        == 403
    )
    assert client.get("/api/profile").status_code == 200


def test_swagger_documents_profile_deletion(client):
    operation = client.get("/openapi.json").json()["paths"]["/api/profile"]["delete"]
    assert "204" in operation["responses"]
    assert "409" in operation["responses"]
    assert any(
        parameter["in"] == "header" and parameter["name"] == "X-CSRF-Token"
        for parameter in operation["parameters"]
    )
