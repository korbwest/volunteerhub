from datetime import UTC, datetime, timedelta

import jwt
from conftest import login, register


def test_register_login_and_logout(client):
    response = register(client)
    assert response.status_code == 201
    assert "password" not in response.text
    assert client.get("/api/auth/me").status_code == 401
    headers = login(client)
    assert client.get("/api/auth/me").json()["user"]["role"] == "VOLUNTEER"
    assert client.post("/api/auth/logout").status_code == 403
    assert client.post("/api/auth/logout", headers=headers).status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_duplicate_email_and_invalid_role(client):
    assert register(client).status_code == 201
    assert register(client, email="VOLUNTEER@example.com").status_code == 409
    assert register(client, email="other@example.com", role="ADMIN").status_code == 422
    assert (
        client.post(
            "/api/auth/login",
            json={"email": "volunteer@example.com", "password": "wrong"},
            headers={"Origin": "http://testserver"},
        ).status_code
        == 401
    )


def test_login_csrf_and_expiry(client):
    register(client)
    assert (
        client.post(
            "/api/auth/login",
            json={"email": "volunteer@example.com", "password": "StrongPassword123!"},
            headers={"Origin": "https://evil.example"},
        ).status_code
        == 403
    )
    token = jwt.encode(
        {"sub": "1", "csrf": "x", "exp": datetime.now(UTC) - timedelta(seconds=1)},
        "test-only-secret-" * 4,
        algorithm="HS256",
    )
    client.cookies.set("session", token)
    assert client.get("/api/auth/me").status_code == 401


def test_organizer_requires_name(client):
    assert register(client, role="ORGANIZER").status_code == 201
    headers = login(client)
    assert (
        client.patch("/api/profile", json={"role": "VOLUNTEER"}, headers=headers).status_code == 422
    )
