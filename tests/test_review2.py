"""Public access and direct authorization checks preserve the car-site boundary."""

import pytest

from app import database
from app.rag_generation import GenerationError, generate, validate_answer
from app.rag_store import CorpusError, approved_sources


def csrf(client):
    """Obtain the actual session synchronizer token."""
    return {"X-CSRF-Token": client.get("/api/csrf").json()["csrf_token"]}


@pytest.mark.parametrize("path", ["/portfolio", "/portfolio/projects/rag", "/rag"])
def test_public_features(client, path):
    response = client.get(path)
    assert response.status_code == 200
    assert 'href="/"' in response.text
    assert "Car Builders" in response.text
    assert response.headers["content-security-policy"]


def test_import_permissions_and_current_role(client, settings, monkeypatch):
    """Direct API calls cannot bypass auth, current roles, or CSRF."""
    called = []
    monkeypatch.setattr(
        client.app.state.rag_store,
        "ingest",
        lambda: called.append(1) or {"status": "imported"},
    )
    assert client.post("/api/rag/import").status_code == 401
    credentials = {
        "username": "rag_member",
        "password": "disposable assistant passphrase",
    }
    assert (
        client.post("/api/signup", json=credentials, headers=csrf(client)).status_code
        == 201
    )
    assert (
        client.post("/api/login", json=credentials, headers=csrf(client)).status_code
        == 200
    )
    assert client.post("/api/rag/import", headers=csrf(client)).status_code == 403
    assert database.set_role(settings, "rag_member", "admin")
    assert client.post("/api/rag/import").status_code == 403
    assert client.post("/api/rag/import", headers=csrf(client)).status_code == 200
    assert (
        client.post(
            "/api/rag/import", json={"path": "/etc/passwd"}, headers=csrf(client)
        ).status_code
        == 400
    )
    assert (
        client.post(
            "/api/rag/import", content=iter([b"out-of-scope"]), headers=csrf(client)
        ).status_code
        == 400
    )
    assert database.set_role(settings, "rag_member", "member")
    assert client.post("/api/rag/import", headers=csrf(client)).status_code == 403
    assert called == [1]


def test_question_bounds_rate_and_empty_evidence(client):
    assert client.post("/api/rag/ask", json={"question": "x" * 1001}).status_code == 422
    assert (
        client.post(
            "/api/rag/ask", json={"question": "okay", "path": "/etc/passwd"}
        ).status_code
        == 422
    )
    assert client.post("/api/rag/ask", content=b"x" * 8193).status_code == 413
    for _ in range(5):
        response = client.post(
            "/api/rag/ask", json={"question": "Where are the builds?"}
        )
        assert response.status_code == 200
        assert response.json()["generation"] == "not-called"
        assert response.json()["insufficient"] is True
    assert (
        client.post(
            "/api/rag/ask", json={"question": "Where are the builds?"}
        ).status_code
        == 429
    )
    assert client.get("/rag/sources/not-real").status_code == 404


def test_unknown_citations_rejected_and_abstention_normalized():
    evidence = [{"id": "CBP-S01-v1-hash-1"}]
    with pytest.raises(ValueError):
        validate_answer(
            {"answer": "Invented", "citations": ["CBP-S99"], "insufficient": False},
            evidence,
        )
    with pytest.raises(ValueError):
        validate_answer(
            {"answer": "No citation", "citations": [], "insufficient": False}, evidence
        )
    with pytest.raises(ValueError):
        validate_answer(
            {
                "answer": "Inline [CBP-S99]",
                "citations": [evidence[0]["id"]],
                "insufficient": False,
            },
            evidence,
        )
    answer = validate_answer(
        {"answer": "Unsupported extra text", "citations": [], "insufficient": True},
        evidence,
    )
    assert answer["answer"] == "Insufficient evidence in the approved corpus."


def test_missing_credentials_and_approval(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(GenerationError, match="not configured"):
        generate("Where are builds?", [])
    monkeypatch.setenv("GEMINI_API_KEY", "test-only-not-a-key")
    monkeypatch.delenv("RAG_PROVIDER_APPROVED", raising=False)
    with pytest.raises(GenerationError, match="approval is pending"):
        generate("Where are builds?", [])


def test_original_allowlist():
    sources = approved_sources()
    assert {s["id"] for s in sources} == {f"CBP-S0{i}" for i in range(1, 6)}
    assert all(s["sha256"] and s["permission"] for s in sources)


def test_manifest_rejects_path_and_permission(tmp_path):
    import json

    source = approved_sources()[0]
    for change in [
        {"file": "../secret.md"},
        {"permission": "pending"},
        {"version": "latest"},
    ]:
        (tmp_path / "manifest.json").write_text(json.dumps([dict(source, **change)]))
        with pytest.raises(CorpusError):
            approved_sources(tmp_path)


def test_manifest_rejects_nonobject(tmp_path):
    """Invalid manifest entries fail validation before any activation."""
    import json

    (tmp_path / "manifest.json").write_text(json.dumps(["not a source object"]))
    with pytest.raises(CorpusError):
        approved_sources(tmp_path)
