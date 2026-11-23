# Additive RAG HTTP contract

The car application's existing instructor contracts are unchanged.

| Method/path | Access/input | Result |
|---|---|---|
| GET `/portfolio` | Public | Responsive portfolio HTML |
| GET `/portfolio/projects/rag` | Public | RAG case study and actual index count |
| GET `/rag` | Public | Question UI, limits/scope/privacy copy; admin-only import control |
| GET `/rag/sources/{id}` | Public, exact indexed ID | Escaped immutable passage/provenance; 404 unknown ID |
| POST `/api/rag/ask` | Public JSON `{ "question": "..." }`, 3–1000 characters, no extra fields, body ≤8192 bytes | 200 answer/insufficient + citations + trace; 422 invalid schema; 413 body too large; 429 limit/busy; 503 semantic/provider unavailable |
| POST `/api/rag/import` | Current authenticated admin, synchronizer `X-CSRF-Token`, empty body | 200 imported/unchanged + documents/chunks/generation; 401 anonymous; 403 member/missing CSRF; 400 invalid input/manifest; 503 unavailable runtime |

`trace` contains selected document ID, immutable chunk ID/version, title, cosine score and controlled source URL. Vector similarity is not factual verification. Generation receives only top-three passages scoring at least 0.30. The tiny fixed evaluation does not establish this threshold universally.

Successful generation returns `answer`, `insufficient`, `citations` (id/title/url objects), `trace`, and `generation=gemini`. With no sufficiently relevant context, generation is not called and the response says insufficient evidence. With no credentials or a provider failure, HTTP 503 returns a safe `detail`, available retrieval `trace`, and `generation=unavailable`; it never substitutes a fabricated answer. A model-declared unsupported answer is normalized to the fixed insufficient-evidence message. Invalid/retrieved-mismatched citations invalidate the response. Every returned citation is a retrieved ID; human claim-support review remains necessary.

One worker allows one generation at a time. Persisted limits allow five questions per minute per socket peer and 100 attempted generations per UTC day. Behind the existing proxy the socket peer is shared, so five/minute is conservatively shared across visitors. Forwarded headers cannot spoof identity; a trusted-proxy per-client limiter is future work. No question text is stored. Credentials stay in the server environment and errors do not echo provider response bodies.

The public API cannot select an import path, upload text, change model/key configuration, access private accounts, expose Chroma, or change roles. A server administrator can edit the fixed manifest and original guides, bump versions, deploy the reviewed source, and import. All active entries are public permitted project text. Old citations remain addressable; current vector and keyword retrieval use one activated generation.
