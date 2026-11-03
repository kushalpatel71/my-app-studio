"""Request-level regressions for expiry, privacy and protected HTML logout."""

import re
import time

from fastapi.testclient import TestClient
import jwt
import pytest

from app import database, security
from app.main import create_app


def _csrf(client):
    return {"X-CSRF-Token": client.get("/api/csrf").json()["csrf_token"]}


def _member(client, username):
    credentials = {"username": username, "password": "disposable route test passphrase"}
    assert (
        client.post("/api/signup", json=credentials, headers=_csrf(client)).status_code
        == 201
    )
    assert (
        client.post("/api/login", json=credentials, headers=_csrf(client)).status_code
        == 200
    )


@pytest.mark.parametrize("expiry", ["server", "jwt"])
def test_expired_session_denies_actual_private_routes(client, settings, expiry):
    """Both token expiry and server expiry reject API and HTML dashboard access."""
    _member(client, "expiry_member")
    if expiry == "server":
        with database.connect(settings) as connection:
            connection.execute("UPDATE sessions SET expires_at = 0")
    else:
        token = client.cookies.get(settings.cookie_name)
        claims = jwt.decode(token, options={"verify_signature": False})
        claims["exp"] = int(time.time()) - 1
        expired = jwt.encode(
            claims,
            settings.secret,
            algorithm="HS256",
            headers={"typ": security.TOKEN_TYPE},
        )
        client.cookies.clear()
        client.cookies.set(settings.cookie_name, expired)
    assert client.get("/api/me").status_code == 401
    response = client.get("/dashboard", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
    assert "expiry_member" not in response.text


def test_private_dashboard_shows_only_the_current_member(client, settings):
    """Two independent sessions must not expose another member's identity."""
    _member(client, "first_member")
    with TestClient(create_app(settings), base_url=settings.origin) as other:
        _member(other, "second_member")
        first = client.get("/dashboard")
        second = other.get("/dashboard")
        assert "first_member" in first.text and "second_member" not in first.text
        assert "second_member" in second.text and "first_member" not in second.text
        assert set(client.get("/api/me").json()) == {"id", "username", "role"}
        assert first.headers["cache-control"] == "no-store"
        assert "password_hash" not in first.text


def test_html_logout_requires_csrf_and_keeps_session_on_rejection(client):
    """A rejected state change cannot silently log a member out."""
    _member(client, "logout_member")
    assert client.get("/logout").status_code == 405
    assert client.post("/logout", data={}).status_code == 403
    assert client.get("/api/me").status_code == 200
    dashboard = client.get("/dashboard")
    token = re.search(r'name="csrf_token" value="([^"]+)"', dashboard.text).group(1)
    response = client.post(
        "/logout", data={"csrf_token": token}, follow_redirects=False
    )
    assert response.status_code == 303
    assert client.get("/api/me").status_code == 401
