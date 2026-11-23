"""Real CPU embeddings/Chroma checks, executed by the dedicated RAG CI job.

The ordinary car environment may omit requirements-rag.txt; skipped here is
explicit, never evidence of a real semantic check. No generation is mocked here.
"""

import json
import shutil
import subprocess
import sys

import pytest

from app.rag_store import CORPUS, CorpusError, RagStore

pytest.importorskip(
    "chromadb", reason="Install requirements-rag.txt for real RAG tests"
)


@pytest.fixture(scope="module")
def index(tmp_path_factory):
    store = RagStore(tmp_path_factory.mktemp("real-rag"))
    assert store.ingest()["documents"] == 5
    return store


def test_real_embedding_and_idempotency(index):
    before = index.stats()
    assert before == {"documents": 5, "chunks": 18}
    assert len(index.embedder(["build navigation"])[0]) == 384
    assert index.ingest()["status"] == "unchanged"
    assert index.stats() == before
    assert all(
        sum(index.embedder.tokenizer.encode(p["text"]).attention_mask) <= 200
        for p in index.retrieve("View Details")
    )


@pytest.mark.parametrize(
    "question, expected",
    [
        ("Where does View Details take me?", "CBP-S01"),
        ("Where can I look at the upgrades on one example car?", "CBP-S01"),
        ("Which role may access the administration page?", "CBP-S04"),
        ("What does the suspension category describe in this assistant?", "CBP-S03"),
    ],
)
def test_semantic_and_keyword(index, question, expected):
    for keyword in [False, True]:
        result = index.retrieve(question, keyword=keyword)
        assert result[0]["source_id"] == expected
        assert all(index.source(p["id"])["text"] == p["text"] for p in result)


def test_unanswerable_retrieves_scope_not_measurement(index):
    result = index.retrieve(
        "What measured horsepower gain will this build give my car?"
    )
    assert result[0]["source_id"] == "CBP-S05"
    assert "insufficient evidence" in result[0]["text"].lower()


def test_changed_removed_and_invalid_source(index, tmp_path):
    corpus = tmp_path / "corpus"
    shutil.copytree(CORPUS, corpus)
    old = index.retrieve("View Details")[0]
    path = corpus / "navigation.md"
    path.write_text(
        path.read_text() + "\n\nThe navigation guide has a revised explanation.\n"
    )
    with pytest.raises(CorpusError, match="new source version"):
        index.ingest(corpus)
    manifest = json.loads((corpus / "manifest.json").read_text())
    manifest[0]["version"] = "v2"
    (corpus / "manifest.json").write_text(json.dumps(manifest))
    assert index.ingest(corpus)["status"] == "imported"
    assert all(
        p["version"] == "v2"
        for p in index.retrieve("View Details")
        if p["source_id"] == "CBP-S01"
    )
    assert index.source(old["id"])["text"] == old["text"]
    (corpus / "manifest.json").write_text(json.dumps(manifest[1:]))
    assert index.ingest(corpus)["documents"] == 4
    assert all(p["source_id"] != "CBP-S01" for p in index.retrieve("View Details"))
    active = index.active()
    manifest[0]["permission"] = "not approved"
    (corpus / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(CorpusError):
        index.ingest(corpus)
    assert index.active() == active
    # Restore the original fixture for the independent process persistence check.
    index.ingest()


def test_restart_persistence_in_new_process(index):
    script = "from app.rag_store import RagStore; import json,sys; s=RagStore(sys.argv[1]); print(json.dumps({'stats':s.stats(),'top':s.retrieve('View Details')[0]['source_id']}))"
    result = subprocess.run(
        [sys.executable, "-c", script, str(index.directory)],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    assert data == {"stats": {"documents": 5, "chunks": 18}, "top": "CBP-S01"}
