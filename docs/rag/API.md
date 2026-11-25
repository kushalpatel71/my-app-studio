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

Successful generation returns `answer`, `insufficient`, `citations` (id/title/url objects), `trace`, and `generation=gemini`. With no sufficiently relevant context, generation is not called and the response says insufficient evidence. With no credentials or a provider failure, HTTP 503 returns a safe `detail`, stable `error_code`, available retrieval `trace`, and `generation=unavailable`; it never substitutes a fabricated answer. A model-declared unsupported answer is normalized to the fixed insufficient-evidence message. Invalid/retrieved-mismatched citations invalidate the response. Every returned citation is a retrieved ID; human claim-support review remains necessary.

One worker allows one generation at a time. Persisted limits allow five questions per minute per resolved client bucket and 100 attempted generations per UTC day. By default the socket peer is the bucket: the existing deployment therefore conservatively shares five/minute across visitors. Review 3 adds opt-in `RAG_TRUSTED_PROXY_IPS` accepting exact IP addresses only. X-Forwarded-For is read only from that trusted socket, walking right-to-left to the nearest untrusted address; forged left prefixes do not replace the actual client appended by the edge. Malformed/duplicate/oversized headers fall back to the socket; Forwarded and X-Real-IP never override it. Enable only after checking the proxy appends/sanitizes actual client information and has no insecure/trusted-unreviewed forwarding configuration. A changed proxy IP safely reverts to the shared bucket; limits, global daily budget and one-generation lock remain unchanged. No shared proxy setting is changed. No question text is stored. Credentials stay in the server environment and errors do not echo provider response bodies.

The public API cannot select an import path, upload text, change model/key configuration, access private accounts, expose Chroma, or change roles. A server administrator can edit the fixed manifest and original guides, bump versions, deploy the reviewed source, and import. All active entries are public permitted project text. Old citations remain addressable; current vector and keyword retrieval use one activated generation.

Review 3 source pages derive file, heading, line and end-exclusive Unicode character spans from retained LF-normalized/stripped Markdown. Original raw SHA-256 and citation IDs remain unchanged. Repeated or unmatched text is labeled ambiguous/unresolved instead of asserting a false location; no database migration/re-embedding is required. Provider errors expose only controlled categories (`missing-key`, `unapproved-project`, `invalid-model`, `provider-http`, `provider-timeout`, `provider-network`, `invalid-evidence`), never raw responses. JSON Schema requests constrain output shape and retrieved citation IDs; independent server validation still rejects invalid output. Schema cannot prove factual support.
