import pytest
from conftest import login, register
from sqlalchemy.orm import Session
from test_projects import payload

from app.models import Project


@pytest.mark.parametrize("status", ["DRAFT", "PUBLISHED"])
def test_owner_can_delete_project(client, status):
    register(client, role="ORGANIZER")
    headers = login(client)
    project_id = client.post("/api/projects", json=payload(), headers=headers).json()["id"]
    if status == "PUBLISHED":
        client.post(f"/api/projects/{project_id}/status", json={"status": status}, headers=headers)
    response = client.delete(f"/api/projects/{project_id}", headers=headers)
    assert response.status_code == 204
    assert response.content == b""
    assert client.get(f"/api/projects/{project_id}").status_code == 404
    assert client.get("/api/my/projects").json()["total"] == 0
    with Session(client.app.state.engine) as db:
        assert db.get(Project, project_id) is None
    assert client.delete(f"/api/projects/{project_id}", headers=headers).status_code == 404


def test_archived_project_cannot_be_deleted(client):
    register(client, role="ORGANIZER")
    headers = login(client)
    project_id = client.post("/api/projects", json=payload(), headers=headers).json()["id"]
    client.post(f"/api/projects/{project_id}/status", json={"status": "ARCHIVED"}, headers=headers)
    assert client.delete(f"/api/projects/{project_id}", headers=headers).status_code == 409
    assert client.get(f"/api/projects/{project_id}").status_code == 200


def test_delete_requires_session_csrf_and_owner(client):
    register(client, role="ORGANIZER")
    headers = login(client)
    project_id = client.post("/api/projects", json=payload(), headers=headers).json()["id"]
    path = f"/api/projects/{project_id}"
    assert client.delete(path, headers={"Origin": "http://testserver"}).status_code == 403
    assert client.delete(path, headers={**headers, "X-CSRF-Token": "wrong"}).status_code == 403
    assert client.delete(path, headers={**headers, "Origin": "http://other"}).status_code == 403
    client.cookies.clear()
    assert client.delete(path, headers=headers).status_code == 401
    register(client, email="other@example.com", role="ORGANIZER")
    assert client.delete(path, headers=login(client, "other@example.com")).status_code == 404
    register(client, email="reader@example.com")
    assert client.delete(path, headers=login(client, "reader@example.com")).status_code == 403
    assert client.get(path, headers=login(client)).status_code == 200


def test_swagger_documents_delete_and_csrf_header(client):
    operation = client.get("/openapi.json").json()["paths"]["/api/projects/{project_id}"]["delete"]
    assert "204" in operation["responses"]
    assert any(
        parameter["in"] == "header" and parameter["name"] == "X-CSRF-Token"
        for parameter in operation["parameters"]
    )
