"""Real HTTP client against an explicit local Postman simulation only."""

import os

import pytest

from app import rag_generation
from app.features import review2
from app.rag_generation import GenerationError
from app.rag_store import RagStore

pytestmark = pytest.mark.skipif(
    not os.getenv("RAG_SIMULATION_URL"), reason="Requires local Postman simulation"
)


@pytest.fixture
def simulated_provider(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "local-simulation-only")
    monkeypatch.setenv("RAG_PROVIDER_APPROVED", "free-tier-confirmed")
    monkeypatch.setattr(rag_generation, "API_BASE", os.environ["RAG_SIMULATION_URL"])
    monkeypatch.setattr(rag_generation, "PROVIDER_TIMEOUT", 0.2)
    return [
        {
            "id": "CBP-S01-v1-fixture-1",
            "text": "View Details opens an individual sample build detail page.",
        }
    ]


@pytest.mark.parametrize(
    "suffix, expected",
    [
        ("SIM_INVALID", "invalid evidence"),
        ("SIM_ERROR", "Generation failed"),
        ("SIM_TIMEOUT", "timed out"),
    ],
)
def test_real_http_provider_failure(simulated_provider, suffix, expected):
    with pytest.raises(GenerationError, match=expected):
        rag_generation.generate("View Details " + suffix, simulated_provider)


def test_real_http_provider_success_and_abstention(simulated_provider):
    result = rag_generation.generate(
        "Where does View Details take me?", simulated_provider
    )
    assert result["citations"] == [simulated_provider[0]["id"]]
    assert result["insufficient"] is False
    result = rag_generation.generate("SIM_UNSUPPORTED", simulated_provider)
    assert result["insufficient"] is True
    assert result["citations"] == []


def test_real_embedding_to_simulated_generation_and_source(
    client, tmp_path, simulated_provider, monkeypatch
):
    """Real import/vectors + simulated HTTP generation, never a real Gemini claim."""
    index = RagStore(tmp_path / "pipeline")
    assert index.ingest()["documents"] == 5
    client.app.state.rag_store = index
    response = client.post(
        "/api/rag/ask", json={"question": "Where does View Details take me?"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["generation"] == "gemini"
    assert data["trace"][0]["source_id"] == "CBP-S01"
    assert data["citations"][0]["id"] in {p["id"] for p in data["trace"]}
    source = client.get(data["citations"][0]["url"])
    assert source.status_code == 200
    assert "View Details opens an individual sample build detail page" in source.text
    monkeypatch.delenv("GEMINI_API_KEY")
    response = client.post(
        "/api/rag/ask", json={"question": "Where does View Details take me?"}
    )
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]
    assert response.json()["trace"]
    # Verify an actual HTTP timeout traverses the public handler too.
    monkeypatch.setenv("GEMINI_API_KEY", "local-simulation-only")
    monkeypatch.setattr(
        review2, "generate", lambda q, p: rag_generation.generate(q + " SIM_TIMEOUT", p)
    )
    response = client.post(
        "/api/rag/ask", json={"question": "Where does View Details take me?"}
    )
    assert response.status_code == 503
    assert "timed out" in response.json()["detail"]
