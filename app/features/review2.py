"""Additive public portfolio/chat and server-authorized corpus administration."""

import hashlib
import json
from pathlib import Path
import threading
import time

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app import security
from app.rag_generation import GenerationError, generate
from app.rag_store import CorpusError, RagStore

router = APIRouter()


class Question(BaseModel):
    """No arbitrary files, URLs, provider settings or tools are accepted."""

    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=3, max_length=1000)


def store(request):
    """Keep test and production indexes alongside their own isolated app data."""
    return request.app.state.rag_store


def initialize(application, settings):
    """Do not load/download embeddings during ordinary car-site startup."""
    application.state.rag_store = RagStore(Path(str(settings.database) + ".rag"))
    application.state.rag_generation_lock = threading.Lock()
    application.include_router(router)


def page(request, template, **context):
    """Render escaped HTML under the existing security headers."""
    return request.app.state.templates.TemplateResponse(
        request=request, name=template, context=context
    )


@router.get("/portfolio", include_in_schema=False)
def portfolio(request: Request):
    """The professional introduction is public."""
    return page(request, "portfolio.html")


@router.get("/portfolio/projects/rag", include_in_schema=False)
def case_study(request: Request):
    """Expose implementation decisions and honest operational status."""
    return page(request, "rag_case.html", stats=store(request).stats())


@router.get("/rag", include_in_schema=False)
def chat_page(request: Request):
    """Public interface; import controls still require server authorization."""
    return page(request, "rag.html", stats=store(request).stats())


@router.get("/rag/sources/{ident}", include_in_schema=False)
def source_page(request: Request, ident: str):
    """Resolve only indexed corpus IDs, never paths or user-supplied URLs."""
    source = store(request).source(ident)
    if not source:
        raise HTTPException(404, "Source not found.")
    return page(request, "rag_source.html", source=source)


@router.post("/api/rag/import")
def import_corpus(request: Request):
    """Admin-only, CSRF-protected import of the fixed approved directory."""
    security.require_admin(request)
    security.require_csrf(request, request.headers.get("x-csrf-token"))
    if request.headers.get("content-length", "0") not in {"0", ""}:
        raise HTTPException(400, "Import does not accept uploaded content or paths.")
    try:
        return store(request).ingest()
    except (CorpusError, UnicodeError, json.JSONDecodeError) as error:
        raise HTTPException(
            400, "Corpus validation failed; active index unchanged."
        ) from error
    except (ImportError, RuntimeError, OSError) as error:
        raise HTTPException(
            503, "Embedding/index service unavailable; check server setup."
        ) from error


@router.post("/api/rag/ask")
def ask(request: Request, question: Question):
    """Embed → retrieve → bounded model context → validate citations."""
    index = store(request)
    now = int(time.time())
    # Trust the socket peer, never an arbitrary client-controlled forwarding header.
    peer = request.client.host if request.client else "unknown"
    bucket = hashlib.sha256(peer.encode()).hexdigest()
    if not index.consume(bucket, now // 60 * 60, 5):
        raise HTTPException(429, "Question limit reached. Try again in a minute.")
    try:
        passages = index.retrieve(question.question.strip())
    except (ImportError, RuntimeError, OSError) as error:
        raise HTTPException(
            503, "Semantic search unavailable; check server setup."
        ) from error
    trace = [
        {
            k: p[k]
            for k in ("id", "source_id", "version", "title", "score", "metric", "url")
        }
        for p in passages
    ]
    selected = [p for p in passages if p["score"] >= 0.30]
    if not selected:
        return {
            "answer": "Insufficient evidence in the approved corpus.",
            "citations": [],
            "insufficient": True,
            "trace": trace,
            "generation": "not-called",
        }
    if not request.app.state.rag_generation_lock.acquire(blocking=False):
        raise HTTPException(429, "Another answer is being generated. Please retry.")
    try:
        if not index.consume("generation-daily", now // 86400 * 86400, 100):
            raise HTTPException(429, "Daily generation limit reached.")
        output = generate(question.question, selected)
    except GenerationError as error:
        return JSONResponse(
            {"detail": str(error), "trace": trace, "generation": "unavailable"},
            status_code=503,
        )
    finally:
        request.app.state.rag_generation_lock.release()
    sources = {p["id"]: p for p in selected}
    output["citations"] = [
        {"id": ident, "title": sources[ident]["title"], "url": sources[ident]["url"]}
        for ident in output["citations"]
    ]
    return dict(output, trace=trace, generation="gemini")
