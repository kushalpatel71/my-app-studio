"""Security and failure regression cases; provider transport is isolated, not Gemini."""

import json
from concurrent.futures import ThreadPoolExecutor

import httpx
import pytest
from fastapi.testclient import TestClient
from starlette.requests import Request

from app import rag_generation
from app.rag_generation import GenerationError
from app.rag_identity import client_identity, trusted_proxy_ips
from app.rag_store import source_location


def request(peer, headers):
    return Request(
        {
            "type": "http",
            "client": (peer, 123),
            "headers": [(k.encode(), v.encode()) for k, v in headers],
        }
    )


@pytest.mark.parametrize(
    "headers,expected",
    [
        ([("x-forwarded-for", "203.0.113.8")], "203.0.113.8"),
        ([("x-forwarded-for", "198.51.100.99, 203.0.113.8")], "203.0.113.8"),
        ([("x-forwarded-for", "2001:db8::8")], "2001:db8::8"),
        ([("x-forwarded-for", "invalid")], "172.18.0.4"),
        (
            [("x-forwarded-for", "203.0.113.8"), ("x-forwarded-for", "198.51.100.9")],
            "172.18.0.4",
        ),
        ([("x-forwarded-for", "172.18.0.4")], "172.18.0.4"),
        (
            [("forwarded", "for=203.0.113.8"), ("x-real-ip", "203.0.113.9")],
            "172.18.0.4",
        ),
    ],
)
def test_trusted_chain_and_forged_prefix(headers, expected):
    assert (
        client_identity(request("172.18.0.4", headers), trusted_proxy_ips("172.18.0.4"))
        == expected
    )
    # The same headers can never override an untrusted socket.
    assert (
        client_identity(
            request("198.51.100.2", headers), trusted_proxy_ips("172.18.0.4")
        )
        == "198.51.100.2"
    )
    assert client_identity(request("172.18.0.4", headers), frozenset()) == "172.18.0.4"


@pytest.mark.parametrize("value", ["*", "0.0.0.0/0", "hosting-web", "172.18.0.0/16"])
def test_proxy_configuration_rejects_broad_trust(value):
    with pytest.raises(ValueError):
        trusted_proxy_ips(value)


def test_distinct_clients_and_forgery_cannot_reset_limit(client):
    app = client.app
    app.state.rag_trusted_proxies = trusted_proxy_ips("172.18.0.4")
    with TestClient(
        app, base_url="http://127.0.0.1:8000", client=("172.18.0.4", 123)
    ) as proxied:
        for _ in range(5):
            assert (
                proxied.post(
                    "/api/rag/ask",
                    json={"question": "Where are builds?"},
                    headers={"X-Forwarded-For": "203.0.113.8"},
                ).status_code
                == 200
            )
        assert (
            proxied.post(
                "/api/rag/ask",
                json={"question": "Where are builds?"},
                headers={"X-Forwarded-For": "198.51.100.99, 203.0.113.8"},
            ).status_code
            == 429
        )
        assert (
            proxied.post(
                "/api/rag/ask",
                json={"question": "Where are builds?"},
                headers={"X-Forwarded-For": "203.0.113.9"},
            ).status_code
            == 200
        )
    with TestClient(
        app, base_url="http://127.0.0.1:8000", client=("198.51.100.2", 123)
    ) as direct:
        for i in range(5):
            assert (
                direct.post(
                    "/api/rag/ask",
                    json={"question": "Where are builds?"},
                    headers={"X-Forwarded-For": f"203.0.113.{i}"},
                ).status_code
                == 200
            )
        assert (
            direct.post(
                "/api/rag/ask",
                json={"question": "Where are builds?"},
                headers={"X-Forwarded-For": "203.0.113.100"},
            ).status_code
            == 429
        )


def test_small_concurrent_counter_is_bounded_and_persistent(client):
    index = client.app.state.rag_store
    with ThreadPoolExecutor(max_workers=3) as pool:
        accepted = list(
            pool.map(lambda _: index.consume("isolated-concurrency", 0, 5), range(9))
        )
    assert sum(accepted) == 5
    from app.rag_store import RagStore

    assert not RagStore(index.directory).consume("isolated-concurrency", 0, 5)


@pytest.mark.parametrize(
    "body",
    [
        None,
        [],
        {"candidates": []},
        {"candidates": [{"content": {"parts": [None]}}]},
        {"candidates": [{"content": {"parts": [{"text": "not json"}]}}]},
    ],
)
def test_malformed_provider_output_is_safe(monkeypatch, body):
    _provider(monkeypatch, lambda r: httpx.Response(200, json=body))
    with pytest.raises(GenerationError) as failure:
        rag_generation.generate(
            "View Details", [{"id": "CBP-S01-v1-test-1", "text": "Public navigation"}]
        )
    assert failure.value.code == "invalid-evidence"


def _provider(monkeypatch, handler):
    monkeypatch.setenv("GEMINI_API_KEY", "local-test-only-secret")
    monkeypatch.setenv("RAG_PROVIDER_APPROVED", "free-tier-confirmed")
    original = httpx.Client
    monkeypatch.setattr(
        rag_generation.httpx,
        "Client",
        lambda **kw: original(transport=httpx.MockTransport(handler), **kw),
    )


@pytest.mark.parametrize(
    "failure,code",
    [
        ("http", "provider-http"),
        ("timeout", "provider-timeout"),
        ("network", "provider-network"),
    ],
)
def test_provider_failure_categories_never_echo_sensitive_body(
    monkeypatch, failure, code
):
    def handler(req):
        if failure == "timeout":
            raise httpx.ReadTimeout("private-provider-debug", request=req)
        if failure == "network":
            raise httpx.ConnectError("private-provider-debug", request=req)
        return httpx.Response(429, text="private-provider-debug local-test-only-secret")

    _provider(monkeypatch, handler)
    with pytest.raises(GenerationError) as caught:
        rag_generation.generate(
            "View Details", [{"id": "CBP-S01-v1-test-1", "text": "Public navigation"}]
        )
    assert caught.value.code == code
    assert "private-provider-debug" not in str(caught.value)
    assert "local-test-only-secret" not in str(caught.value)


def test_schema_constrains_citations_but_local_validation_still_rejects(monkeypatch):
    def handler(req):
        payload = json.loads(req.content)
        schema = payload["generationConfig"]["responseJsonSchema"]
        assert schema["properties"]["citations"]["items"]["enum"] == [
            "CBP-S01-v1-test-1"
        ]
        assert req.headers["x-goog-api-key"] == "local-test-only-secret"
        assert "local-test-only-secret" not in str(req.url)
        return httpx.Response(
            200,
            json={
                "candidates": [
                    {
                        "content": {
                            "parts": [
                                {
                                    "text": json.dumps(
                                        {
                                            "answer": "Invented",
                                            "citations": ["CBP-S99"],
                                            "insufficient": False,
                                        }
                                    )
                                }
                            ]
                        }
                    }
                ]
            },
        )

    _provider(monkeypatch, handler)
    with pytest.raises(GenerationError) as failure:
        rag_generation.generate(
            "View Details", [{"id": "CBP-S01-v1-test-1", "text": "Public navigation"}]
        )
    assert failure.value.code == "invalid-evidence"


def test_source_location_offsets_and_honest_ambiguity():
    provenance = {
        "text": "# Heading\n\nSome  original\nwords.\n\nOther paragraph.",
        "file": "original.md",
    }
    found = source_location(provenance, "Heading\nSome original words.")
    assert (
        found["status"] == "located"
        and found["start_line"] == 3
        and found["end_line"] == 4
    )
    excerpt = provenance["text"][found["start_char"] : found["end_char"]]
    assert " ".join(excerpt.split()) == "Some original words."
    assert (
        source_location(
            {"text": "Repeated.\n\nRepeated.", "file": "x.md"}, "Heading\nRepeated."
        )["status"]
        == "ambiguous"
    )


def test_symlink_manifest_is_outside_allowlist(tmp_path):
    from app.rag_store import CorpusError, approved_sources

    external = tmp_path / "outside.json"
    external.write_text("[]")
    root = tmp_path / "corpus"
    root.mkdir()
    try:
        (root / "manifest.json").symlink_to(external)
    except OSError:
        pytest.skip("Platform does not allow creating symlinks")
    with pytest.raises(CorpusError, match="manifest"):
        approved_sources(root)
