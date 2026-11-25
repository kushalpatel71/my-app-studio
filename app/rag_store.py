"""Versioned, allowlisted public corpus and private persistent semantic index."""

# Lazy optional dependencies keep the existing car app usable without RAG extras.
# pylint: disable=import-error,not-callable


from functools import cached_property
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import threading

CORPUS = Path(__file__).resolve().parents[1] / "docs/rag/corpus"
MODEL = "all-MiniLM-L6-v2"
INDEX_CONFIG = "minilm-onnx-cosine-wordpiece200-v1"


class CorpusError(ValueError):
    """A corpus cannot be activated safely."""


def approved_sources(root=CORPUS):
    """Validate the entire manifest before embedding or activating any records."""
    manifest_path = root / "manifest.json"
    if root.is_symlink() or manifest_path.is_symlink():
        raise CorpusError(
            "The approved corpus root or manifest cannot be a symbolic link."
        )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, list) or not 1 <= len(manifest) <= 5:
        raise CorpusError("Expected one to five approved documents.")
    sources, seen = [], set()
    for item in manifest:
        if not isinstance(item, dict):
            raise CorpusError("Each source must be a provenance object.")
        required = {"id", "title", "version", "file", "origin", "permission", "author"}
        if not required <= item.keys():
            raise CorpusError("Missing provenance fields.")
        if not all(isinstance(item[k], str) and item[k] for k in required):
            raise CorpusError("Invalid provenance fields.")
        if not re.fullmatch(r"CBP-S0[1-5]", item["id"]) or item["id"] in seen:
            raise CorpusError("Invalid or duplicate source ID.")
        if not re.fullmatch(r"v[1-9][0-9]*", item["version"]):
            raise CorpusError("Invalid version.")
        if item["permission"] != "original-project-text-public-and-provider-context":
            raise CorpusError("Unapproved document.")
        path = root / item["file"]
        if (
            path.is_symlink()
            or path.suffix != ".md"
            or path.resolve().parent != root.resolve()
            or not path.is_file()
        ):
            raise CorpusError("Only allowlisted Markdown in the corpus is allowed.")
        raw = path.read_bytes()
        if not 1 <= len(raw) <= 20000:
            raise CorpusError("Document size outside allowed bounds.")
        text = raw.decode("utf-8").replace("\r\n", "\n").strip()
        if "<" in text or "\x00" in text:
            raise CorpusError("Corpus must be plain Markdown, without HTML.")
        sources.append(dict(item, text=text, sha256=hashlib.sha256(raw).hexdigest()))
        seen.add(item["id"])
    return sources


def source_location(provenance, passage):
    """Locate an exact normalized passage body without changing existing IDs.

    Offsets are Unicode character offsets in the retained LF-normalized, stripped
    Markdown, not raw-byte offsets. Ambiguous repeated bodies are not guessed.
    """
    body = passage.partition("\n")[2]
    pattern = r"\s+".join(re.escape(word) for word in body.split())
    matches = list(re.finditer(pattern, provenance["text"])) if pattern else []
    if len(matches) != 1:
        return {"status": "ambiguous" if matches else "unresolved"}
    match = matches[0]
    text = provenance["text"]
    return {
        "status": "located",
        "file": provenance["file"],
        "heading": passage.partition("\n")[0],
        "start_char": match.start(),
        "end_char": match.end(),
        "start_line": text.count("\n", 0, match.start()) + 1,
        "end_line": text.count("\n", 0, match.end()) + 1,
        "coordinate_system": "LF-normalized stripped Markdown; Unicode characters",
    }


class RagStore:
    """Chroma is a library, never a publicly exposed database service."""

    def __init__(self, directory, embedder=None):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.lock = threading.RLock()
        self._embedder = embedder
        self._client = None
        with self.connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT);
                CREATE TABLE IF NOT EXISTS chunks
                (id TEXT PRIMARY KEY, source TEXT, version TEXT, title TEXT,
                 text TEXT, provenance TEXT, generation TEXT);
                CREATE VIRTUAL TABLE IF NOT EXISTS keywords USING fts5(id UNINDEXED,
                  generation UNINDEXED, text);
                CREATE TABLE IF NOT EXISTS limits
                (bucket TEXT, window INTEGER, count INTEGER,
                 PRIMARY KEY(bucket, window));
            """)

    def connect(self):
        """A separate database; account records never enter retrieval."""
        return sqlite3.connect(self.directory / "manifest.sqlite3", timeout=20)

    @property
    def embedder(self):
        """Lazy CPU ONNX MiniLM avoids loading PyTorch into the web service."""
        if self._embedder is None:
            from chromadb.utils.embedding_functions import (  # pylint: disable=import-outside-toplevel
                ONNXMiniLM_L6_V2,
            )

            class SingleCpuMiniLM(
                ONNXMiniLM_L6_V2
            ):  # pylint: disable=too-few-public-methods
                """Bound ONNX thread pools instead of detecting the host CPU count."""

                @cached_property
                def model(self):
                    """Create one CPU-only inference session with bounded threads."""
                    options = self.ort.SessionOptions()
                    options.intra_op_num_threads = 1
                    options.inter_op_num_threads = 1
                    options.log_severity_level = 3
                    options.graph_optimization_level = (
                        self.ort.GraphOptimizationLevel.ORT_ENABLE_ALL
                    )
                    return self.ort.InferenceSession(
                        str(
                            self.DOWNLOAD_PATH
                            / self.EXTRACTED_FOLDER_NAME
                            / "model.onnx"
                        ),
                        sess_options=options,
                        providers=["CPUExecutionProvider"],
                    )

            self._embedder = SingleCpuMiniLM(
                preferred_providers=["CPUExecutionProvider"]
            )
        return self._embedder

    @property
    def client(self):  # pylint: disable=import-outside-toplevel
        """Open persistent Chroma only when retrieval/import needs it."""
        if self._client is None:
            import chromadb  # pylint: disable=import-outside-toplevel

            self._client = chromadb.PersistentClient(
                path=str(self.directory / "chroma"),
                settings=chromadb.config.Settings(anonymized_telemetry=False),
            )
        return self._client

    def active(self):
        """One committed generation is visible at a time."""
        with self.connect() as db:
            row = db.execute("SELECT value FROM state WHERE key='active'").fetchone()
        return row[0] if row else None

    def chunk(self, source):
        """Keep heading/paragraph boundaries; enforce the real tokenizer cap."""
        # ONNX's model download loads its pinned tokenizer before chunking.
        self.embedder([source["title"]])
        tokenizer = self.embedder.tokenizer
        records, heading = [], source["title"]
        for paragraph in re.split(r"\n\s*\n", source["text"]):
            if paragraph.startswith("#"):
                heading = paragraph.lstrip("# ").strip()
                continue
            words = paragraph.split()
            while words:
                size = len(words)
                while size > 0:
                    text = heading + "\n" + " ".join(words[:size])
                    if sum(tokenizer.encode(text).attention_mask) <= 200:
                        break
                    size -= 1
                if not size:
                    raise CorpusError("A word or heading exceeds the token limit.")
                records.append(text)
                words = words[size:]
        if not records:
            raise CorpusError("Document has no passages.")
        return records

    def ingest(self, root=CORPUS):
        """Stage a complete snapshot, then atomically switch the active manifest."""
        with self.lock:
            sources = approved_sources(root)
            signature = json.dumps(sources, sort_keys=True) + INDEX_CONFIG
            generation = hashlib.sha256(signature.encode()).hexdigest()[:24]
            if generation == self.active():
                return {"status": "unchanged", "generation": generation, **self.stats()}
            with self.connect() as db:
                for source in sources:
                    old = db.execute(
                        "SELECT provenance FROM chunks "
                        "WHERE source=? AND version=? LIMIT 1",
                        (source["id"], source["version"]),
                    ).fetchone()
                    if old and json.loads(old[0]) != source:
                        raise CorpusError(
                            "Changed bytes/provenance require a new source version."
                        )
            records = []
            for source in sources:
                for ordinal, passage in enumerate(self.chunk(source), 1):
                    ident = (
                        f'{source["id"]}-{source["version"]}-'
                        f'{source["sha256"][:12]}-{ordinal}'
                    )
                    records.append((ident, source, passage))
            collection = self.client.get_or_create_collection(
                "snapshot-" + generation,
                metadata={"hnsw:space": "cosine"},
                embedding_function=None,
            )
            texts = [r[2] for r in records]
            vectors = self.embedder(texts)
            collection.upsert(
                ids=[r[0] for r in records], embeddings=vectors, documents=texts
            )
            with self.connect() as db:
                db.execute("DELETE FROM keywords WHERE generation=?", (generation,))
                for ident, source, passage in records:
                    db.execute(
                        "INSERT OR REPLACE INTO chunks VALUES (?,?,?,?,?,?,?)",
                        (
                            ident,
                            source["id"],
                            source["version"],
                            source["title"],
                            passage,
                            json.dumps(source),
                            generation,
                        ),
                    )
                    db.execute(
                        "INSERT INTO keywords VALUES (?,?,?)",
                        (ident, generation, passage),
                    )
                db.execute(
                    "INSERT OR REPLACE INTO state VALUES ('active',?)", (generation,)
                )
            return {"status": "imported", "generation": generation, **self.stats()}

    def stats(self):
        """Count only the activated corpus."""
        with self.connect() as db:
            docs, chunks = db.execute(
                "SELECT count(DISTINCT source), count(*) FROM chunks "
                "WHERE generation=?",
                (self.active(),),
            ).fetchone()
        return {"documents": docs, "chunks": chunks}

    def source(self, ident):
        """Immutable historical citations remain readable by controlled ID lookup."""
        with self.connect() as db:
            row = db.execute(
                "SELECT source,version,title,text,provenance FROM chunks WHERE id=?",
                (ident,),
            ).fetchone()
        if not row:
            return None
        return {
            "id": ident,
            "source_id": row[0],
            "version": row[1],
            "title": row[2],
            "text": row[3],
            "provenance": json.loads(row[4]),
            "location": source_location(json.loads(row[4]), row[3]),
            "url": "/rag/sources/" + ident,
        }

    def retrieve(self, question, keyword=False):
        """Return the same active source records for vector and FTS5 comparison."""
        with self.lock:
            active = self.active()
            if not active:
                return []
            if keyword:
                terms = re.findall(r"[a-zA-Z0-9]+", question)[:40]
                if not terms:
                    return []
                expression = " OR ".join('"' + term + '"' for term in terms)
                with self.connect() as db:
                    rows = db.execute(
                        "SELECT id,bm25(keywords) FROM keywords WHERE keywords MATCH ? "
                        "AND generation=? ORDER BY bm25(keywords) LIMIT 3",
                        (expression, active),
                    ).fetchall()
                return [
                    dict(self.source(ident), score=-score, metric="fts5-bm25")
                    for ident, score in rows
                ]
            collection = self.client.get_collection(
                "snapshot-" + active, embedding_function=None
            )
            result = collection.query(
                query_embeddings=self.embedder([question]),
                n_results=min(3, collection.count()),
            )
            return [
                dict(self.source(ident), score=round(1 - distance, 5), metric="cosine")
                for ident, distance in zip(result["ids"][0], result["distances"][0])
            ]

    def consume(self, bucket, window, maximum):
        """Persistent counters enforce limits across app restarts (one worker)."""
        with self.lock, self.connect() as db:
            db.execute("DELETE FROM limits WHERE window < ?", (window - 172800,))
            db.execute("INSERT OR IGNORE INTO limits VALUES (?,?,0)", (bucket, window))
            count = db.execute(
                "SELECT count FROM limits WHERE bucket=? AND window=?", (bucket, window)
            ).fetchone()[0]
            if count >= maximum:
                return False
            db.execute(
                "UPDATE limits SET count=count+1 WHERE bucket=? AND window=?",
                (bucket, window),
            )
            return True
