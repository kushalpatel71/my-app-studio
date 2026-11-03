"""Admin resources must not expose session internals or accept revoked sessions."""

from app import database


def _csrf(client):
    return {"X-CSRF-Token": client.get("/api/csrf").json()["csrf_token"]}


def _admin(client, settings):
    credentials = {
        "username": "role_member",
        "password": "disposable role test passphrase",
    }
    assert (
        client.post("/api/signup", json=credentials, headers=_csrf(client)).status_code
        == 201
    )
    assert (
        client.post("/api/login", json=credentials, headers=_csrf(client)).status_code
        == 200
    )
    assert database.set_role(settings, "role_member", "admin")


def test_admin_api_only_returns_own_public_identity(client, settings):
    """The role helper includes session state, which must stay out of API output."""
    _admin(client, settings)
    response = client.get("/api/admin")
    assert response.status_code == 200
    assert set(response.json()) == {"detail", "user"}
    assert set(response.json()["user"]) == {"id", "username", "role"}
    assert response.json()["user"]["username"] == "role_member"
    assert response.json()["user"]["role"] == "admin"
    assert "session_id" not in response.text
    assert "password_hash" not in response.text
    assert response.headers["cache-control"] == "no-store"


def test_logout_revokes_access_to_admin_resources(client, settings):
    """A saved admin cookie cannot regain access after ordinary account logout."""
    _admin(client, settings)
    saved = client.cookies.get(settings.cookie_name)
    assert client.post("/api/logout", headers=_csrf(client)).status_code == 200
    client.cookies.set(settings.cookie_name, saved)
    assert client.get("/api/admin").status_code == 401
    response = client.get("/admin", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
