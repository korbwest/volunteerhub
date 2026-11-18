from conftest import login, register


def payload(**changes):
    return {
        "title": "Помощь приюту",
        "city": "Ульяновск",
        "location": "ул. Мира, 1",
        "starts_at": "2027-01-01T10:00:00+04:00",
        "duration": 2,
        "duration_unit": "HOURS",
        "description": "Помощь животным и уборка территории.",
        "category": "ANIMALS",
        "cover_url": "https://example.com/cover.jpg",
        **changes,
    }


def test_project_lifecycle_and_visibility(client):
    register(client, role="ORGANIZER")
    headers = login(client)
    response = client.post("/api/projects", json=payload(), headers=headers)
    assert response.status_code == 201, response.text
    project_id = response.json()["id"]
    assert client.get("/api/projects").json()["total"] == 0
    assert (
        client.post(
            f"/api/projects/{project_id}/status", json={"status": "PUBLISHED"}, headers=headers
        ).status_code
        == 200
    )
    assert (
        client.get(
            "/api/projects", params={"search": "ПРИЮТ", "city": "Ульяновск", "category": "ANIMALS"}
        ).json()["total"]
        == 1
    )
    assert client.get("/api/projects", params={"city": "Казань"}).json()["total"] == 0
    assert client.get("/api/projects", params={"page": 2}).json()["items"] == []
    assert (
        client.post(
            f"/api/projects/{project_id}/status", json={"status": "ARCHIVED"}, headers=headers
        ).status_code
        == 200
    )
    assert client.get("/api/my/projects").json()["total"] == 1
    assert (
        client.patch(
            f"/api/projects/{project_id}", json=payload(title="Новое"), headers=headers
        ).status_code
        == 409
    )
    assert (
        client.post(
            f"/api/projects/{project_id}/status", json={"status": "PUBLISHED"}, headers=headers
        ).status_code
        == 409
    )
    client.cookies.clear()
    assert client.get(f"/api/projects/{project_id}").status_code == 404


def test_roles_ownership_and_profile_privacy(client):
    register(client, role="ORGANIZER")
    owner_headers = login(client)
    project_id = client.post("/api/projects", json=payload(), headers=owner_headers).json()["id"]
    client.cookies.clear()
    assert client.get(f"/api/projects/{project_id}").status_code == 404
    register(client, email="other@example.com", role="ORGANIZER")
    headers = login(client, "other@example.com")
    assert (
        client.patch(f"/api/projects/{project_id}", json=payload(), headers=headers).status_code
        == 404
    )
    register(client, email="third@example.com")
    headers = login(client, "third@example.com")
    assert client.post("/api/projects", json=payload(), headers=headers).status_code == 403
    assert (
        client.patch(
            "/api/profile", json={"name": "Новое имя", "city": "Самара"}, headers=headers
        ).status_code
        == 200
    )
    assert client.get("/api/profile").json()["city"] == "Самара"
    orgs = client.get("/api/organizations").json()
    assert orgs["total"] == 2
    assert "email" not in str(orgs)
    assert "password" not in str(orgs)


def test_validation_and_csrf(client):
    register(client, role="ORGANIZER")
    headers = login(client)
    assert client.post("/api/projects", json=payload()).status_code == 403
    assert (
        client.post("/api/projects", json=payload(duration=0), headers=headers).status_code == 422
    )
    assert (
        client.post(
            "/api/projects", json=payload(starts_at="2027-01-01T10:00:00"), headers=headers
        ).status_code
        == 422
    )
    assert (
        client.post("/api/projects", json=payload(title="   "), headers=headers).status_code == 422
    )
    assert (
        client.get(
            "/api/projects", params={"date_from": "2027-02-01", "date_to": "2027-01-01"}
        ).status_code
        == 422
    )
    assert client.get("/api/projects", params={"page_size": 1000}).status_code == 422


def test_cover_url_respects_database_limit(client):
    register(client, role="ORGANIZER")
    headers = login(client)
    url = "https://example.com/" + "x" * 1990
    assert (
        client.post("/api/projects", json=payload(cover_url=url), headers=headers).status_code
        == 422
    )


def test_archive_serializes_concurrent_edit(client):
    from concurrent.futures import ThreadPoolExecutor, TimeoutError

    import pytest
    from sqlalchemy import select
    from sqlalchemy.orm import Session

    from app.models import Project

    engine = client.app.state.engine
    if engine.dialect.name != "postgresql":
        pytest.skip("Row lock regression requires PostgreSQL")
    register(client, role="ORGANIZER")
    headers = login(client)
    project_id = client.post("/api/projects", json=payload(), headers=headers).json()["id"]
    with Session(engine) as transaction, ThreadPoolExecutor(max_workers=1) as executor:
        row = transaction.scalar(select(Project).where(Project.id == project_id).with_for_update())
        future = executor.submit(
            client.patch, f"/api/projects/{project_id}", json=payload(title="Race"), headers=headers
        )
        try:
            with pytest.raises(TimeoutError):
                future.result(timeout=0.5)
        finally:
            row.status = "ARCHIVED"
            transaction.commit()
        assert future.result(timeout=10).status_code == 409
