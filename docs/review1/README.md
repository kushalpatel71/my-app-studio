# IS373 Reviews 1–2 — evolving individual project record

Review 1 Plan due **November 17, 2026, 1:00 PM Eastern**. Review 2 Build deadline supplied by Canvas: **December 1, 2026, 1:00 PM Eastern**. Build audit/checks: November 23, 2026.
Owner: Kushal Patel. This is the single individual record; extend its two sections through Build, Checked Release and Improve. Research and implementation are AI-assisted. The portfolio and RAG pipeline are now implemented and checked locally as detailed below. Live deployment approval and real Gemini credentials/free-tier confirmation are pending; no working hosted RAG journey or peer feedback is claimed. Earlier Plan prose is retained as historical evidence, not current implementation status.

[Repository](https://github.com/kushalpatel71/my-app-studio) · [Plan branch](https://github.com/kushalpatel71/my-app-studio/tree/feature/review1-plan) · [Issue #7](https://github.com/kushalpatel71/my-app-studio/issues/7) · [PR #8](https://github.com/kushalpatel71/my-app-studio/pull/8) (merged November 23, 2026 at `1efd73e`)

## Instructor requirements and repository audit

**Review 2 access note (November 23):** the supplied current portfolio, individual and milestones pages returned a 114-byte client redirect stub to `/lander`; the GitHub source fallbacks returned 404. Their current contents could not be re-read. This Build follows the full Canvas requirements supplied in the task, including the authoritative December 1, 1 PM Eastern deadline. Prior November 9 source-reading notes below remain historical.

All five required pages were read on November 9 using direct HTTPS retrieval after browser-tool errors:
[milestones/rubric](https://kaw393939.github.io/is373-studio/course/milestones.html), [career handout](https://kaw393939.github.io/is373-studio/handouts/career-research.html), [database/RAG handout](https://kaw393939.github.io/is373-studio/handouts/database-rag-research.html), [record template](https://kaw393939.github.io/is373-studio/templates/project-record.html), [Plan example](https://kaw393939.github.io/is373-studio/examples/plan.html).
The Plan requires research, alternatives, a justified design and expected checks. A hosted link is optional at Plan. Canvas remains authoritative for the assignment box and deadline.

Audited latest remote `main`: [`15eaa35f87ed405d9dba3716a290f180d9fa4984`](https://github.com/kushalpatel71/my-app-studio/commit/15eaa35f87ed405d9dba3716a290f180d9fa4984). Fresh clone had a clean tree; `feature/review1-plan` was created from that revision. Read [README](../../README.md), [AGENTS](../../AGENTS.md), [SPEC](../../SPEC.md), [LEARNING](../../LEARNING.md), all three [lessons](../lessons/), source, security/database helpers, request/browser tests, contracts and CI. Origin is now `git@github.com:kushalpatel71/my-app-studio.git`; this is the student's public repository, not the instructor template.

| Stage | Real implementation and acceptance evidence | GitHub state verified through connector |
|---|---|---|
| APP-001 | [Showcase router](../../app/showcase.py), [brand/sample data](../../app/brand.json), templates/CSS, [route tests](../../tests/test_showcase.py), [homepage contracts](../../contracts/test_homepage.py), [browser journeys](../../tests/browser/test_browser.py). Home, build index, three detail pages, About; unknown slug 404; Next Step retained. | [Issue #1](https://github.com/kushalpatel71/my-app-studio/issues/1), [PR #2](https://github.com/kushalpatel71/my-app-studio/pull/2) merged at `fedd07c`. |
| APP-002 | [Accounts](../../app/features/accounts.py), [security](../../app/security.py), [SQLite database](../../app/database.py), [account contracts](../../contracts/test_accounts.py), [route tests](../../tests/test_account_routes.py). Signup member-only, hashing, HttpOnly JWT session, CSRF, private dashboard, server revocation at logout. | [Issue #3](https://github.com/kushalpatel71/my-app-studio/issues/3), [PR #4](https://github.com/kushalpatel71/my-app-studio/pull/4) merged at `e4f0753`. |
| APP-003 | [Roles](../../app/features/roles.py), [role contracts](../../contracts/test_roles.py), [admin tests](../../tests/test_admin_routes.py). Anonymous API 401, member 403, admin allowed; current database role overrides stale JWT role; trusted CLI changes affect existing sessions. | [Issue #5](https://github.com/kushalpatel71/my-app-studio/issues/5), [PR #6](https://github.com/kushalpatel71/my-app-studio/pull/6) merged at `15eaa35`. |

All three implementations are present on main; [studio.json](../../studio.json) declares `implemented_through: 3`. Historical SPEC/LEARNING contain stale pending/open language, including contradictory merge notes. Actual merged PR metadata and Git history establish integration; old prose is not treated as current status. Prior learner observations/AI help are attributed only to those existing records; this audit does not independently prove understanding or authorship. Current check receipt is recorded below. No existing application, test, contract, marker, workflow, SPEC or LEARNING content is changed by this Plan.

### 1. Individual portfolio + career research

#### Review 2 Build — current implementation, November 23, 2026

**Status:** public portfolio implemented at `/portfolio`; RAG case study at `/portfolio/projects/rag`. **Hosted portfolio URL: not yet deployed/verified.** The proposed hostname in the Docker runbook is not a live-link claim. [Build issue #9](https://github.com/kushalpatel71/my-app-studio/issues/9); branch `feature/review2-build`, based on merged Review 1 main `1efd73e16552abf3336e0dd897c903300225db82`.

- [Portfolio template](../../app/templates/portfolio.html), [case study](../../app/templates/rag_case.html), [additive routes](../../app/features/review2.py), and scoped CSS implement the evidence-first layout. NJIT student/developer identity and provisional AI Application / Product Engineering direction come from the owner’s task. No employment, credentials or independent AI expertise is invented.
- About, Skills, Projects, Research and Contact anchors work by keyboard. Working links connect the existing car website, RAG case study, assistant, GitHub profile, application source, account/role PRs and project record. Car Builders Place remains at `/`; its build index/details, About, account, dashboard, logout and current-role behavior remain intact.
- Car Builders Place’s case study points to actual FastAPI/authentication/authorization/SQLite/test work. RAG’s case study identifies five original guides, actual index count, retrieval flow, ONNX adaptation, checks and limitations. Group Content System remains **contribution evidence pending**: no verified group repo/task/diff was supplied, and no group files were modified. No individual group contribution is fabricated.
- Review 1’s GovWell research emphasized grounded AI/evaluation; that finding motivated inspectable retrieved IDs, sources and explicit operational status. The Palantir comparison motivated reviewable delivery decisions. Evidence-first usefulness to recruiters is still a hypothesis, not a peer-tested result.
- GitHub is the supplied public professional link. Dedicated public email/contact route awaits approval; LinkedIn and résumé are omitted because none was supplied. No inferred address from server configuration is published.

**Actual checks:** the full `python3 studio.py check` passed Black/Pylint, 120 application/request tests (110 previous + 10 new), 18 unchanged instructor contracts through APP-003, and 15 real Chromium cases (11 previous + 4 new). The base Python 3.14 run explicitly skipped the optional real-Chroma module and five local-simulation cases; they ran separately under Python 3.12, as recorded in section 2. New browser cases verify anonymous access, anchor navigation, case-study → assistant links, 1440/390/320px layout without horizontal overflow, keyboard activation, answer/submit state with an empty test corpus, and a failed-network UI fixture. The UI fixture is not real generation. AI visually inspected actual desktop/mobile renders; no student observation is inferred. A separate browser run with the real index displayed missing-key failure, exposed cosine trace `CBP-S01-v1-40f3df8f794e-2` / `0.4277`, and opened its indexed source.

**Implemented / unfinished:** routes, layout, evidence links, accurate labels and accessible controls are implemented. Dedicated contact information, verified group contribution, optional professional links, user/peer review and public hosting are unfinished. The individual record remains this file; historical Review 1 research follows.

**Changed:** added public portfolio/case study and cross-navigation without replacing the car site. **Checked:** actual local regression, keyboard/layout cases, rendered pages and real retrieval-source opening. **Next:** approve the isolated existing-server deployment; supply public contact/group evidence; verify HTTPS and a real reader task. **My contributions / AI assistance:** owner selected the scope, topic, preservation constraints, provisional direction and Docker/Traefik requirement. AI authored code, corpus, tests, research synthesis and this factual record. Personal understanding/interpretation remains not yet evidenced for this Build; no fabricated reflection or peer review fills that gap.

#### Historical Review 1 portfolio research and plan

**Historical Plan status (November 9):** Research and Plan drafted; student reflection/selection review pending. The earlier November 24 Build date is superseded by the supplied Canvas December 1 deadline.

#### Research: three original employer records

These saved evidence notes summarize original employer-hosted postings checked **2026-11-09**. Direct HTTPS retrieval succeeded for all three. Palantir and GovWell include public JobPosting JSON-LD; Datadog includes readable posting/application text. The browser index also supplied matching descriptions, but direct original content was checked to avoid relying only on search snippets. No screenshots or applications were created. Public research summaries are suitable for this record; personal eligibility judgments and full career reflection stay private. These three examples do not establish market trends.

**J1 — Palantir Technologies, “Forward Deployed Software Engineer, New Grad - Commercial.”** Enterprise software; FDE family. [Original posting](https://jobs.lever.co/palantir/2e6b0ac8-83e9-4be5-a3aa-cf319f751728).

- Status: page/application available on check date; future vacancy unconfirmed. JSON-LD posted June 13, 2025; deadline not stated.
- New York, NY; full-time, hybrid; new graduate. Travel expectation 25–50% depending on team/location. Requires December 2026 or Spring 2027 graduation; student's graduation/work authorization and sponsorship eligibility unverified.
- Responsibilities: collaborate on architecture; build customer-specific applications/LLM workflows; manage stakeholder relationships through delivery.
- Required: engineering degree, programming proficiency, specified graduation window. Preferred degree fields include computing, engineering, mathematics and related sciences. “What We Value” emphasizes autonomy, ambiguity and customer outcomes; it is not a separate mandatory credential list.
- Supporting excerpt, “What We Require”: “Must be graduating in December 2026 or Spring 2027.”
- Existing evidence: Python/FastAPI application and server permission boundaries in APP-002/003 above; no enterprise customer delivery claimed.
- Gap: customer discovery/delivery experience. Proposed action by **November 12**: write three discovery questions for an actual portfolio reviewer and confirm graduation/travel eligibility privately.

**J2 — GovWell, “AI Product Engineer.”** Government software; AI product/application family. [Original posting](https://jobs.ashbyhq.com/GovWell/7c4cff34-bd8d-41d7-a54b-8f9ee0d96ac3/).

- Status: active posting metadata with direct application on check date; future vacancy unconfirmed. JSON-LD posted February 24, 2026; deadline not stated.
- New York, NY; full-time, hybrid, 3+ office days/week. Numeric seniority/years not stated; production experience makes this a longer-term reference, not verified entry-level eligibility. US location metadata; sponsorship/work authorization not established. Metadata says TELECOMMUTE but prose requires hybrid attendance; follow the more specific prose.
- Responsibilities: improve assistant retrieval/evaluation; prioritize fixes using production usage; ship and iterate AI features.
- Expected qualifications (“Who you are”): production LLM/RAG or evaluation experience, full-stack ability, product judgment and autonomy. No separately labeled preferred list; listed stack is context, not proof every technology is required.
- Supporting excerpt, “Who you are”: “Strong full-stack ability”.
- Existing evidence: FastAPI UI/API, automated account/role tests and iterative showcase delivery. This supports foundations, not existing AI expertise.
- Gap: evaluated retrieval/generation. Proposed action by **November 16**: finalize five expected-source questions and a citation-failure check for the RAG Build.

**J3 — Datadog, “Software Engineering Intern.”** Observability/security software; general software/platform family. [Original posting](https://careers.datadoghq.com/detail/8114186/?gh_jid=8114186&source=relomote.com), requisition 1065.

- Status: original description and application section available on check date; future availability unconfirmed. Posting date/deadline not visible.
- Paris, France; internship, hybrid. Pursuing CS/software engineering/related degree or equivalent practical experience; targeting 2027 full-time start; available six months starting February–June 2027. Student availability, relocation, French work authorization and sponsorship remain unverified; this is a verified internship posting, not a confirmed suitable application.
- Responsibilities: contribute to live observability data systems; improve distributed/cloud services; address performance/reliability/scaling problems.
- Qualifications under “Who You Are”: CS fundamentals, programming, AI-tool experience or interest, degree/equivalent and timing above. No separate preferred-qualification list. Kubernetes is a learning area, not an explicit prerequisite.
- Supporting excerpt, “Who You Are”: “Targeting a 2027 full-time start date”.
- Existing evidence: Python service, automated tests and GitHub PR delivery; no distributed-system scale claimed.
- Gap: distributed-systems observability. Proposed action by **November 13**: sketch request/error/latency measurements for the RAG service and privately verify internship timing/location eligibility.

#### Compare directions and choose the reader

| Direction | Regular work in this sample | Existing evidence | Missing evidence / course experiment |
|---|---|---|---|
| AI application/product engineering | GovWell: user-facing AI features, grounded answers, evaluation and iteration | FastAPI UI/API; security/access checks; documented showcase revision | RAG import/query trace and citations with expected-versus-observed evaluation; no production LLM work yet |
| Forward deployed engineering | Palantir: customer-specific integration, architecture and stakeholder delivery | Bounded application decisions and working account/role implementation | Real discovery, enterprise integration, stakeholder adoption and travel fit; course reviewer task can begin discovery but cannot establish professional FDE experience |

Platform engineering (Datadog) is a third family investigated: useful for reliability learning, with distributed-system depth still missing. **Recommendation:** provisionally target entry-level **AI Application / Product Engineering**, keeping FDE as a comparison. The current artifact evidence is closest to building and checking application behavior; a small RAG evaluation directly addresses the AI gap. This is an AI-assisted fit inference, not a claim that Kushal meets GovWell's experience bar or has confirmed personal travel preferences. The user supplied the provisional interest; personal reasons remain for the private reflection.

**Target reader:** a recruiter or internship reviewer hiring for entry-level AI application development. After viewing the portfolio, the reader should identify the intended direction, inspect one implemented capability, and distinguish completed work from planned AI work and the student's own contribution from AI/team help.

| Employer responsibility | Portfolio evidence today | Clearly labeled future evidence |
|---|---|---|
| GovWell: improve retrieval grounding/evaluation | Existing [test structure](../../tests/) demonstrates application checking only | RAG case study: versioned manifest, retrieved chunk IDs, five actual query results, claim/citation review and one improvement/retest |
| Palantir: build custom applications and make architecture decisions | [Showcase routes](../../app/showcase.py), [SPEC](../../SPEC.md), [PR #2](https://github.com/kushalpatel71/my-app-studio/pull/2) show a bounded enthusiast task and multi-page revision | Real reader discovery note; never label class/AI feedback as enterprise customer work |
| Datadog: own technical delivery with other engineers | [Check workflow](../../.github/workflows/check.yml), merged PRs above and actual checks below | Group case study with named issue/PR, personal diff, reviewer and integrated result; group repository and contribution not yet provided |

#### Plan: same content, two lightweight layouts

Shared content inventory for both options: introduction/direction, evidence-supported skills, individual RAG case study, group contribution case study, repositories/demos/checks, optional resume/LinkedIn, contact.

```text
Option A — Evidence-first (recommended)
Header: Kushal Patel | Projects | About | Contact
Short intro + provisional AI application direction
Featured work: Car Builders Place [implemented] | RAG [planned]
Case studies: task → my contribution/help → decision → evidence → limits
Skills with source links → Group work [pending evidence]
About → GitHub / demo links → optional resume/LinkedIn → contact

Option B — About-me-first
Header: Kushal Patel | About | Projects | Contact
Introduction + interests/direction
About and evidence-supported skills
Same project cards and case studies → same group-work placeholder
Same GitHub / demo links → optional resume/LinkedIn → contact
```

Choose **A** provisionally: it exposes inspectable work early for the target reader. The expected benefit is faster evidence discovery; this is a design hypothesis, not a peer-tested result. B may support a stronger personal narrative, but no employment history or credentials were supplied to populate that narrative. Use readable typography, restrained charcoal/lime accents related to the existing project, clear headings/focus, high contrast and responsive stacking. A practical “builder” voice is proposed; expertise should be demonstrated through links, never invented endorsements.

**Planned implementation/page outline:** reuse FastAPI/Jinja/shared styles on additive `/portfolio` and project-detail routes; leave existing Home/build/account/admin URLs and Next Step intact. Intro identifies the provisional direction without calling planned RAG work a mastered skill. Skills link Python/FastAPI, HTML/CSS, SQLite sessions, authorization and testing to the audited artifacts. Individual case study will show corpus permission, architecture, actual trace, setup and limits once built. Group case study requires a real group repository, task, personal contribution and review evidence; currently placeholder only. GitHub points to this repository. Demo URLs remain “not yet hosted”; no invented domain. Resume and LinkedIn are omitted until supplied. Professional contact is pending a student-approved email or contact URL; do not expose an inferred address.

**Planned observable portfolio checks (not executed):**

1. A reader can find the intended role and one linked implemented artifact from `/portfolio`; headings and links work by keyboard at desktop and 390px.
2. Each skill/case-study claim has a working evidence link and an accurate implemented/planned label; group contribution never implies sole authorship.
3. RAG project link opens a clearly labeled case study and, after Build, its actual chat; placeholder never resembles a working result.
4. Contact/resume/LinkedIn show only supplied, reviewed details; missing optional links are omitted and the chosen contact route is checked before publication.

**Changed:** added three sourced employer notes, comparison, target reader, mapping, two layouts and implementation outline. **Checked:** original postings and repository evidence read; no portfolio usability test or human review performed. **Next:** student confirms direction/layout and privately checks eligibility by November 12; confirm contact and group contribution links by November 16. **My contribution / AI assistance:** user supplied project/repository, constraints and provisional interest; AI researched, audited and drafted recommendations. Student's personal rationale, reflection and understanding have not been supplied and are not fabricated.

**Build / Checked Release / Improve:** pending. Future dates are November 24, December 3 and December 10 respectively; later add actual hosted revision, link/access checks and real peer observation → meaningful fix → retest here.

### 2. Individual RAG app + technical research

#### Review 2 Build — current implementation, November 23, 2026

**Status:** real approved-file ingestion, persistent vectors, semantic retrieval, keyword comparison, source UI and Gemini HTTP integration are implemented. **Hosted RAG URL: not yet deployed/verified. Actual Gemini answer: unavailable — no key or free-tier project confirmation supplied.** A mock is used only in isolated tests; no successful hosted generation is claimed.

**Architecture and compatibility:** retain FastAPI/Jinja and the existing account/security services. Chroma `1.5.9`, ONNX Runtime `1.23.2`, tokenizers `0.23.3`, NumPy `2.5.5` were installed and exercised under Python 3.12.16. The existing Python 3.14 car environment has no matching ONNX Runtime wheel and the original unpinned Sentence Transformers/Chroma installation failed resolution. Use Chroma’s CPU ONNX export of Sentence Transformers `all-MiniLM-L6-v2` rather than the PyTorch-based package. This preserves genuine 384-dimensional neural embeddings while reducing runtime dependencies. ONNX intra/inter-op thread pools are explicitly one thread. Model archive SHA-256 is verified by the pinned Chroma implementation: `913d7300ceae3b2dbc2c50d1de4baacab4be7b9380491c27fab7418616a16ec3`.

[Current official Gemini model documentation](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite) identifies `gemini-3.5-flash-lite` as supported with structured text output. Pricing checked November 23: free input/output on the documented free tier; standard paid rates $0.30 input / $2.50 output per million tokens. No paid project, billing or API usage was enabled. Free-tier content may be used to improve Google products; the chat UI discloses provider transfer. Real account/model/quota access is unverified. Orbit discovery found generateContent but returned an old model example; the current official model documentation governs the identifier. Postman CLI 1.75.0 lacks `status`, and signed-in owner mock search was unavailable; a local contract simulation was built instead. Neither that simulation nor model documentation supplies credentials.

**Chosen comparison:** persistent cosine vectors are the semantic experiment, SQLite FTS5 is the simpler same-corpus keyword baseline. No graph database or hybrid fusion is implemented: the tiny evaluation does not show a retrieval miss requiring them. Both methods put the expected source first for all four supported questions. This does not demonstrate vector superiority; the authored paraphrase guide contains matching vocabulary. Broader queries and independent reader wording remain future evaluation.

**Source/import manifest:** [manifest](../rag/corpus/manifest.json) contains five original AI-authored project guides requested by the owner for this Build. The task explicitly requested original permitted documents and provider context; attribution is not presented as independent student authorship. No third-party photos/manuals/employer prose/private account data is indexed.

| ID | Title / file | Version / permission | Actual chunks |
|---|---|---|---|
| CBP-S01 | [Site navigation](../rag/corpus/navigation.md), checked against showcase routes | v1 / original project text, public/provider context | 3 |
| CBP-S02 | [Understanding sample builds](../rag/corpus/sample-builds.md), checked against brand data | v1 / same permission | 3 |
| CBP-S03 | [Modification categories](../rag/corpus/categories.md), original scope-limited glossary | v1 / same permission | 4 |
| CBP-S04 | [Accounts and access](../rag/corpus/access.md), checked against account/role routes | v1 / same permission | 4 |
| CBP-S05 | [Assistant scope and provenance](../rag/corpus/assistant-scope.md), original policy guide | v1 / same permission | 4 |

Actual index generation: `c8f0e4d840fdef5f40a4f4ec`; **5 documents / 18 chunks**. [Machine-readable retrieval receipt](../rag/retrieval-evidence.json) records executed ranks/IDs/scores. [Importer](../../app/rag_store.py) validates fixed-root UTF-8 Markdown, ≤5 files/20 KB each, unique allowlisted IDs, version/provenance/permission, rejects symlinks/traversal/HTML, cleans CRLF and whitespace, and chunks by heading/paragraph with a real ≤200-word-piece cap. Chunk IDs include source ID/version/hash/ordinal. SQLite stores complete text/provenance/source hash; Chroma persists vectors under a staged snapshot. Activation changes atomically only after staging succeeds. Changed bytes require a version bump; stale/removed sources leave current retrieval, while historical indexed passages remain addressable. Source-span offsets and retention cleanup are not implemented; exact retained passage text and content hashes are available.

**Actual retrieval evidence:** query “Where does View Details take me?” returned:

| Rank | Chunk ID | Cosine similarity |
|---|---|---|
| 1 | `CBP-S01-v1-40f3df8f794e-2` | 0.42770 |
| 2 | `CBP-S02-v1-d8b616f8c5ce-2` | 0.31188 |
| 3 | `CBP-S01-v1-40f3df8f794e-3` | 0.31140 |

Top passage begins “Site navigation” and explains that View Details opens an individual sample build detail page, with the three real detail paths. The source route `/rag/sources/CBP-S01-v1-40f3df8f794e-2` was actually opened in Chromium. Scores are relevance signals, not factual confidence. Top three passages scoring ≥0.30 become bounded provider context. Missing context returns insufficient evidence without a model call.

| Evaluation question/type | Expected | Actual top vector source / cosine | Keyword baseline observation |
|---|---|---|---|
| Where does View Details take me? / exact | Navigation | CBP-S01 / 0.42770 | CBP-S01 first |
| Where can I look at the upgrades on one example car? / paraphrase | Navigation/sample interpretation | CBP-S01 / 0.58849 | CBP-S01 first |
| Which role may access the administration page? / relationship | Access guide, admin role | CBP-S04 / 0.63688 | CBP-S04 first |
| What does the suspension category describe in this assistant? / ordinary | Glossary | CBP-S03 / 0.63739 | CBP-S03 first |
| What measured horsepower gain will this build give my car? / unanswerable | No numeric claim; scope/abstention | CBP-S05 / 0.40816; passage explicitly lacks measurements | CBP-S05 first; real generated abstention pending |

**Generation and security:** [provider boundary](../../app/rag_generation.py) makes a real server-side Gemini REST call only with a key and `RAG_PROVIDER_APPROVED=free-tier-confirmed`. It applies a 20-second timeout, 600-output-token cap, JSON parsing and retrieved-ID validation. Invalid/no citations invalidate a supported answer; an unsupported model answer is normalized to insufficient evidence. Text is escaped in HTML/assigned with `textContent`, never interpreted as model HTML. A valid ID still does not establish every claim’s support; human review remains necessary. [API contract](../rag/API.md) records input/status/trace behavior. Public questioning requires no account; import checks current admin status and existing CSRF. Fixed paths, 8192-byte body cap, 1000-character question limit, persistent five/minute socket-peer and 100/day attempted-generation limits, and a one-generation lock bound public use. Behind Traefik the peer limit is shared across visitors. No questions are retained, no vector/admin database port is exposed, and no private account record enters context. Missing keys, timeouts and provider failures return clear 503 errors with available retrieval traces.

**Executed checks (expected → actual):**

- Full car/application regression: Black/Pylint; 120 application tests, 18 unchanged contracts, 15 Chromium cases passed. Base environment explicitly skips optional dependencies/simulation; skips are not counted as RAG passes.
- Real CPU/Chroma suite: **8 passed**. Five-document import → 5/18; 384-dimensional embedding → 384; repeat import → `unchanged`/same counts; exact/paraphrase/relationship/glossary → expected source ranked first; missing measurement → scope passage; changed bytes without version → rejected; v2 → no current v1 hits; removed source → excluded; invalid permission → active snapshot unchanged; new process → 5/18 and navigation retrieval retained.
- Request/security suite: **10 passed** including public pages, body/schema/rate limits, empty-index abstention, invalid citations, missing key/approval and real auth/CSRF boundary. Anonymous import 401; member 403; promoted admin without CSRF 403; valid admin+CSRF reaches importer; arbitrary path/body 400; demotion on same session 403. The fast permission case uses a recording importer; real ingestion is tested separately.
- Local Postman simulation with the **real HTTP client**: **5 passed**, including HTTP 503 HTML failure, invalid citation, actual delayed-response timeout, supported/insufficient JSON parsing, full real embedding/retrieval → simulated generation → actual source route, public missing-key 503 and timeout 503. Request events confirm generateContent was exercised. Test answer: “View Details opens an individual sample build detail page.” Citation was the actual retrieved `CBP-S01-v1-40f3df8f794e-2`. **This is a simulated answer, not an actual Gemini answer.**
- Actual browser with real index: no horizontal overflow at 1440/390/320px; supported question → honest missing-key 503 + retrieval trace; trace link → exact indexed navigation passage. No live model answer is claimed.

**Docker/hosting:** [production Dockerfile](../../deploy/Dockerfile), [Compose](../../deploy/compose.yml), [private-env example](../../deploy/app.env.example), and [build/deploy/restart/backup/rollback runbook](../../deploy/README.md) are prepared. Read-only existing-server audit confirmed authorized `is373-server` SSH, 1 CPU, 1967 MiB RAM / approximately 1421 MiB available, 44 GiB free disk, existing calculator/Traefik/practical-prod/practical-qa, Docker 29.1.3 and `hosting-web`. Existing proxy uses Docker labels with default HTTPS/Let's Encrypt on `websecure`; no proxy edit is needed. Proposed new isolated app uses one worker, 768 MiB/0.75 CPU cap, non-root/read-only filesystem, no published host port, one persistent named volume and a new noncolliding hostname. Existing services/volumes/routes are preserved. Live infrastructure changes and certificate provisioning await explicit owner approval. A proposed hostname is not a verified hosted URL.

**Local container evidence:** image build executed successfully; Compose validation passed. A quoted tmpfs option was corrected after the first smoke launch rejected the YAML list split; no existing container/volume was deleted. The isolated local production container reached Docker `healthy` and HTTP `/health` returned `{"status":"ok","mode":"production"}`. Real container import returned 5 documents/18 chunks; repeat import was unchanged. Restart retained 5/18 and semantic navigation retrieval. Sampled memory was about 385 MiB while embedding runtime was present and about 54 MiB after the trusted import process exited; these are samples, not peak-load proof. A transient health timeout during initial indexing motivated explicitly bounded ONNX thread pools. Final-image/CI/live measurements will be recorded when executed. No remote container, volume or proxy config has been changed.

**Reproduce:** `python3 studio.py check`; install `requirements-rag.txt` in Python 3.12; run `python -m pytest -q tests/test_rag_real.py tests/test_review2.py`; run `python scripts/evaluate_rag.py --index PRIVATE_INDEX_PATH`. For provider simulation: `postman simulation run postman/simulations/review2-provider.sim.yaml --port 4511 --no-history`, then `RAG_SIMULATION_URL=http://127.0.0.1:4511/gemini/v1beta/models/ python -m pytest -q tests/test_rag_provider_http.py`. No real API key is needed for simulations. `--generate` on the evaluation script explicitly requests actual generation and still requires approved credentials.

**Limitations / December 3 Next:** obtain deployment approval and verify public HTTPS + all existing sites; configure an approved free-tier provider key privately and execute real generated answers/abstention/citation support review; verify backup/restore and measured import/query headroom on the server; supply contact/group evidence and a real student interpretation/reader observation. Improve corpus/query diversity, per-client trusted-proxy limiting, source offsets/retention and failure observability based on measured needs. No peer feedback, personal reflection or understanding is fabricated.

**Changed:** implemented versioned ingestion, actual neural embeddings, persistent Chroma/FTS, public chat/source UI, real Gemini integration, security boundaries, tests and Docker deployment proposal. **Checked:** real import/vector/rank/lifecycle/persistence tests, direct auth/CSRF tests, local HTTP simulation and browser trace/source opening; simulated versus live evidence separated. **Next:** approval-gated deployment and real configured provider journey before claiming hosted completion. **My contributions / AI assistance:** owner supplied car topic, repositories, provisional direction, preservation requirements and Docker/Traefik scope. AI implemented, authored original guides/tests, executed the listed checks and drafted the record. Independent student reasoning and Build peer feedback remain not yet evidenced.

#### Historical Review 1 technical research and plan

**Historical Plan status (November 9):** proposed Car Builds Knowledge Assistant; research/design only at that time. The current Build status above supersedes these earlier planned-implementation statements.

**Reader/task:** a Car Builders Place visitor asks how to navigate the sample builds and how to interpret illustrative modification information. Answer only from approximately five short owner-authored help documents. Exclude repair instructions, safety advice, measured performance, fitment claims and personal/account data. A small informational assistant provides a bounded portfolio case study.

#### Technical research and primary sources

Access date for the sources below: **2026-11-09**. These are research references, not permission to import their text into the corpus.

| Concept / source and relevant section | Explanation and design implication |
|---|---|
| [Lewis et al., RAG paper](https://arxiv.org/abs/2005.11401), abstract | RAG combines retrieval from external indexed evidence with generation. Our planned inference workflow retrieves passages before asking a model to answer; this is not a claim to reproduce the paper's training or results. |
| [Chroma adding data](https://docs.trychroma.com/docs/collections/add-data), Adding Data; [Chroma repository](https://github.com/chroma-core/chroma), Python client examples | A vector database stores embeddings and metadata with identifiable records for similarity retrieval. Chroma's unique IDs/document metadata support provenance. Local persistence/version compatibility must be verified in Build. |
| [MiniLM model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), Intended uses / Usage | Embeddings map text into numeric representations for semantic comparison; they do not verify facts. This model outputs 384 dimensions and truncates beyond 256 word pieces by default. Record model revision/tokenizer and avoid silent truncation. |
| [Neo4j graph concepts](https://neo4j.com/docs/getting-started/appendix/graphdb-concepts/), nodes/relationships/properties | A graph represents entities (build, modification category, document) and typed relationships. Provenance must support every edge; extracted or inferred links can be wrong. |
| [SQLite FTS5](https://www.sqlite.org/fts5.html), Overview / query syntax / BM25 | Keyword search matches indexed terms and can rank passages; SQL filters explicit fields. This is a small reproducible baseline for source IDs and exact terms. |
| [Sentence Transformers models](https://www.sbert.net/docs/sentence_transformer/pretrained_models.html), Loading Models | Query and document encodings must use compatible configuration. Pin the actual model revision and package versions during implementation. |
| [Gemini 3.5 Flash-Lite](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite), model code/capabilities; [pricing](https://ai.google.dev/gemini-api/docs/pricing) | Proposed hosted generation model `gemini-3.5-flash-lite`; text output and structured output are documented. Availability to this account, actual cost and SDK compatibility remain untested. Vendor pricing is variable: check the current tier before enabling calls. |

Source provenance records who authored a document, its version/origin, permission and exact passage location. Import converts approved input into retained originals and cleaned text. Chunking splits that text into evidence units while keeping source mappings. Retrieval chooses relevant permitted units, model context packages those units with IDs, generation drafts an answer, and citations let readers inspect support. Citation validity requires both a real source location and support for the associated claim; a valid-looking ID alone is insufficient.

#### Compare bounded approaches and decide

| Approach | Representation / useful task | Cost and limit for this corpus |
|---|---|---|
| Keyword/SQL baseline | FTS5 passages plus structured source/version fields; exact “View Details” or source IDs | Few dependencies, deterministic inspection; paraphrases can miss wording |
| Vector | Chunk embeddings and cosine similarity; “where can I see the upgrades?” | May help paraphrases, requires model/index storage; nearest neighbor can still be irrelevant |
| Graph | Builds, categories, pages and typed edges; “which page describes this build?” | Explicit relationship traversal is inspectable; manual edge authoring/validation and another database are excessive for five short prose guides |
| Hybrid | Keyword + vector rank fusion with identical source filters, optionally graph traversal | Could retain exact terms and paraphrases; extra tuning and debugging need a measured benefit |

**Decision (proposed ADR R1): vector-first, retrieval-only baseline retained.** FastAPI/Jinja interface, Chroma local persistent store, `sentence-transformers/all-MiniLM-L6-v2` local embeddings, server-side Gemini `gemini-3.5-flash-lite` generation. Separate SQLite manifest/FTS5 database from the existing account database. Use one process/writer initially; no graph database or agent/tool execution. Passage-oriented questions fit vector retrieval; five documents do not justify graph operations. The choice tests a hypothesis about paraphrase retrieval, not a demonstrated improvement. Compare the same five queries using keyword and vector retrieval; add hybrid only if a specific observed miss warrants it.

**Simpler fallback:** SQLite FTS5 + the same generation API and source UI. If no API budget/access is available, provide an explicitly labeled search-only interface with quoted excerpts; it is not a completed RAG chat and does not satisfy the later real-generation Build requirement. Local embedding resource failure can trigger the FTS5 fallback without changing account/security behavior.

#### Proposed corpus and source manifest

All five entries below are **proposed, not authored/imported/permission-verified documents**. The intended author is Kushal Patel, with AI assistance disclosed if used. Their future owner approval must authorize storage, public demo excerpts and sending selected passages to the generation provider. Public repository availability does not alone authorize third-party reuse. No photos, employer text, copyrighted manuals, private reflections, student data, credentials or live account records enter the corpus.

| Stable ID | Proposed version/title and origin | Planned content and permission gate |
|---|---|---|
| CBP-S01 | v1 / Site navigation; planned `docs/rag/corpus/navigation.md` | Owner-authored description of Home, Builds, View Details and About, checked against [router](../../app/showcase.py). Pending author/license approval. |
| CBP-S02 | v1 / Understanding sample builds; planned `docs/rag/corpus/sample-builds.md` | Owner-authored explanation that samples are illustrative and not measured specifications, checked against [brand data](../../app/brand.json). Pending approval; no photo reproduction. |
| CBP-S03 | v1 / Modification categories; planned `docs/rag/corpus/categories.md` | New synthetic glossary of wheels, suspension, engine and performance labels; no vehicle fitment/repair advice. Pending author review/approval. |
| CBP-S04 | v1 / Accounts and access; planned `docs/rag/corpus/access.md` | Owner-authored public signup/login/dashboard/logout/member/admin explanation, checked against [accounts](../../app/features/accounts.py) and [roles](../../app/features/roles.py). Pending approval; exclude account details and promotion procedures. |
| CBP-S05 | v1 / Assistant scope and provenance; planned `docs/rag/corpus/assistant-scope.md` | New owner-approved assistant policy: interpret supplied sample content, expose sources, acknowledge absent measurements. Pending approval. |

Manifest fields to persist: `source_id`, title, author, version, original URI/path, origin type, license/permission evidence and approver/date, access scope, accessed/created date, raw SHA-256, cleaned SHA-256, active status, import outcome, chunking configuration, embedding ID/revision/dimensions and import time. Proposed paths become source URLs only after real files are created. Immutable source versions remain addressable for old citations; current retrieval excludes retired versions. Do not assign fabricated hashes or permission dates now.

#### Import and source-to-answer workflow

```mermaid
flowchart LR
    A[Permitted documents] --> B[Admin import and manifest validation]
    B --> C[Clean text and retain originals/provenance]
    C --> D[Heading and paragraph chunks]
    D --> E[Compatible embeddings]
    E --> F[Persistent Chroma and SQLite manifest]
    Q[Question and access rules] --> R[Retrieve top 3 active permitted chunks]
    F --> R
    R --> G[Bounded model context with chunk IDs]
    G --> H[Generate answer or insufficient evidence]
    H --> I[Validate references and display source passages]
```

Graph alternative for comparison replaces chunks/embeddings with validated entities/relationships and bounded traversal returning supporting passages. It is not a second implemented pipeline.

1. Import allowlisted UTF-8 Markdown only, initially five files ≤20 KB each. Reject missing permission, invalid encoding, duplicate source IDs and out-of-root paths. No arbitrary URL fetching, uploads, PDFs or HTML in the initial scope.
2. Normalize line endings/whitespace; preserve headings, paragraph boundaries and original offsets. Do not remove qualifiers such as “illustrative.” Retain original and cleaned text with hashes.
3. Create deterministic versioned chunk IDs from source/version/section/ordinal and record exact text/span. Build a staging collection and activate a complete index version only after validation, avoiding partially updated results.
4. Repeat identical source/hash/config: report `unchanged` and keep counts/IDs. Changed source: create new version/chunks, retire old current entries atomically. Removed source: deactivate from retrieval, retain versioned source evidence under the retention rule. Re-embedding after model/chunker changes creates a new index version; never mix dimensions/models silently.
5. Question length ≤1,000 characters; retrieve top 3 chunks with active-version/public-scope filters. Apply the same filters before keyword and vector retrieval. Tune relevance/abstention on the small evaluation set, without claiming a universal similarity threshold.
6. Send only selected passages and their IDs, question and a fixed answer policy to the model. Source instructions are untrusted quoted data. Do not enable tools or let the model alter permissions. Require structured answer/claim-to-chunk references; no context means an insufficient-evidence response without an API call.
7. Reject nonexistent or unretrieved citation IDs; source links resolve through a server-controlled ID lookup to immutable passages. Review whether each factual claim is actually supported. Unknown/mismatched citations cause a safe error/abstention, not a fabricated source. Render escaped text and allowlisted links.

#### Representation sketches and chunking comparison

This is a **proposed synthetic sentence**, not imported repository content: “View Details opens an individual sample build page.”

```json
{
  "source_id": "CBP-S01",
  "version": "v1",
  "chunk_id": "CBP-S01:v1:navigation:001",
  "title": "Site navigation",
  "section": "Build details",
  "text": "View Details opens an individual sample build page.",
  "origin": "proposed docs/rag/corpus/navigation.md",
  "permission_status": "pending-owner-approval",
  "access_scope": "public-after-approval",
  "original_span": null,
  "content_sha256": null,
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "embedding_revision": null,
  "embedding_dimensions": 384,
  "embedding": null
}
```

Null values mean not computed, not verified. Numeric vectors must come from a real embedding run. Imports must reject this pending example until provenance/permission fields are complete.

**Graph sketch (comparison only):** `(Document {id:CBP-S01, version:v1}) -[DESCRIBES {support_chunk:CBP-S01:v1:navigation:001}]-> (Page {kind:BuildDetail})`; `(Link {label:View Details}) -[OPENS {support_chunk:...}]-> (Page {kind:BuildDetail})`. Validate each edge against approved text. A build/category `HAS_CATEGORY` edge would need its own explicit evidence; do not infer performance or part compatibility from category labels. Entity identity includes stable IDs; relationship properties retain source/version/span.

| Chunking method | Proposed parameters / trade-off | Worked boundary on a proposed fixture |
|---|---|---|
| Heading + paragraph (selected) | Keep heading with paragraph; cap at 200 word pieces measured with the pinned MiniLM tokenizer; split long paragraphs at sentences; no routine overlap | Keeps “Build details” with the full sentence. Retains semantic context; tiny sections may need title context. |
| Fixed characters | 40-character windows, 8-character overlap for the teaching sketch; later compare 600/100 as an experiment | On `Build details\nView Details opens an individual sample build page.`, first window ends `an indi`; next starts ` an individual...`. Repeats text and can sever the useful phrase. |

The boundary sketch is illustrative; character-window offsets were checked with a small Python string slice, but neither corpus chunker nor a retrieval comparison was executed. Character counts are not tokens. Actual ingestion must measure word pieces and preserve source offsets; the selected 200-word-piece cap leaves room under the model's documented truncation boundary. Inspect real boundary examples during Build, log both methods and choose based on retrieval results.

#### Evaluation questions and observable checks

All expectations depend on authoring the corpus as described; **no queries have run**. Before execution freeze corpus/index/model revisions. Record actual retrieved IDs/ranks, selected context, answer, claim support, opened citation location, latency and token/cost usage where measured. Compare keyword/vector retrieval separately from generation quality.

| Query | Type | Expected source/behavior |
|---|---|---|
| Where does “View Details” take me? | Exact term | CBP-S01 navigation; individual sample detail page |
| Where can I look at the upgrades on one example car? | Paraphrase | CBP-S01 + CBP-S02; explain navigation and illustrative nature |
| Which role may access the administration page? | Relationship/access | CBP-S04; admin role, members denied; no role-change instructions |
| What does the suspension category describe in this assistant? | Ordinary useful question | CBP-S03 glossary only; no real fitment/repair guarantee |
| What measured horsepower gain will this build give my car? | Missing evidence | Explicit insufficient evidence; CBP-S02/CBP-S05 may explain scope but cannot supply a number |

Planned retrieval check: expected relevant source appears in top 3 for each of the four supported questions; record exact source-level hit count out of four and ranks. Planned answer check: every factual claim supported, every citation resolves to the right version/passage, and missing-evidence question has no invented gain. Five questions are a tiny diagnostic set, not proof of general accuracy. Failure leads to inspecting source coverage/chunk boundary/retrieval before changing prompts; rerun the identical query and preserve before/after evidence. CBP-S05's scope rule should also be visible in the UI independently of retrieval.

| Observable user story | Intended check (all unexecuted) |
|---|---|
| Visitor asks a supported question and opens its sources | Answer references only retrieved active permitted chunks; clicking opens exact version/passage; manually verify each claim, plus inject an unknown/wrong citation and require rejection. |
| Visitor asks for absent evidence | Missing horsepower question returns insufficient evidence; unrelated nearest-neighbor chunks cannot justify a number; zero-hit query does not call the model. |
| Admin imports/updates permitted content | Import twice: same IDs/counts and `unchanged`; edit one source: new version without stale current hits; delete: no current retrieval; malformed/missing-permission input rejected without partial activation. Restart retains approved active index and source mappings. |
| Anonymous visitor or member tries administration directly | Anonymous import API 401, member 403, admin permitted with CSRF; direct requests tested independently of hidden buttons; demotion applies to current session; existing APP-001/002/003 checks still pass. |
| Visitor encounters limits or provider failure | Length/rate limits return clear errors; timeout/budget exhaustion shows search/source fallback with generation unavailable label; no key/token/private data in responses/logs and no fabricated answer. |

#### Hosting, resource, cost and security constraints

**No deployment recommended yet.** This repository proves FastAPI/SQLite and GitHub Actions checks. README references a separate Server Studio; it contains no verified Docker/Traefik deployment pipeline, server sizing or live hosting evidence. DigitalOcean/Docker/Traefik experience is user-reported context, not independently audited here. No server target or SSH host was supplied, and no remote resource observation occurred. Local laptop resources do not establish droplet capacity.

Before choosing a deployment target, record the authorized server's vCPU, RAM/free memory, disk/free space, architecture/OS, container limits, existing workload and ports, Docker/Traefik versions, volume/backups and domain/TLS ownership. Suggested read-only measurements after identifying the correct host: `nproc`, `free -h`, `df -h`, `docker stats --no-stream` and container resource configuration. Keep raw infrastructure details/private configuration out of public evidence. Do not change the shared server/proxy during this Plan.

Proposed deployment gate: one CPU worker, persistent private Chroma/manifest volumes and separate existing auth volume; measure peak import/query RSS, disk and idle/load behavior on the actual target and retain at least 30% memory headroom under the agreed workload before approving capacity. Indexing/model dependencies may outweigh the tiny corpus. If insufficient, keep ingestion local or use the simpler retrieval design and remeasure; no GPU or local generation model is assumed. Verify backup/restore and restart persistence before release. Docker/Traefik can be reused only after this audit; do not expose the database port or Docker socket. GitHub Actions currently checks code; deployment would need a separately reviewed workflow.

Proposed bounds: five ≤20 KB documents, one import at a time, top 3 passages, ≤2,000 context tokens and ≤400 output tokens, one generation request at a time, 20-second provider timeout, 5 requests/minute/session plus an app-wide daily cap. Select an application-enforced **$5/month maximum** only after student approval; this is a proposed ceiling, not a price quote or current spend. Estimate `(input tokens × current input rate + output tokens × current output rate)` with the vendor's unit scaling, then log actual usage and stop before the approved cap. Free tier/quota, billing access and generation credentials are not confirmed. Never assume provider budget alerts enforce a hard cap.

Keep API credentials server-side in ignored environment/secret storage; no browser key, Git history or CI log exposure. Existing auth signing keys/account database are not retrieval inputs. Import requires current server admin checks and CSRF. Use permitted public sample text only; review provider data-handling terms before sending passages. Redact request logs, avoid retaining user questions by default, use no external tool execution, prevent arbitrary file/URL access, and treat source prompt injection as data. Rate limits are application controls, not proof of complete security.

**Changed:** added technical research, comparisons, ADR, five proposed sources/manifest, representations, workflow, chunking alternatives, expected queries, stories and conditional hosting plan. **Checked:** original technical sources read and app boundaries inspected; no RAG code/model/API/query or resource benchmark executed. **Next:** student approves/authors corpus and confirms permissions by November 13; review architecture/budget/credentials and identify server for resource audit by November 16; implement only after this Plan review. **My contribution / AI assistance:** user proposed the Car Builds topic and reuse constraints; AI researched and drafted architecture/checks. No student technical explanation or implementation result is inferred from acceptance of a proposal.

**Build / Checked Release / Improve:** pending. November 24 requires a real small hosted import → retrieval → chat journey and hosted portfolio foundation. December 3 adds persistent hosted service, actual query evaluation and repeatable setup. December 10 requires a real peer task/observation, meaningful change and retest. Neither planned checks nor AI critique count as executed evaluation or human peer feedback.

## Verification and Plan rubric crosswalk

| Criterion (25 points each; no self-assigned grade) | Current evidence / remaining limit |
|---|---|
| Complete | Both exact individual headings; three postings, comparison/map/two layouts; RAG manifest/architecture/import/evaluation/hosting plan. Planned source permissions and student review are explicit. |
| Thoughtful | Employer responsibilities motivate evidence-first layout; vector/graph/baseline/hybrid compared; bounded decision and simpler fallback. Fit/performance are hypotheses. |
| Checked | Original pages/direct posting evidence, actual merged PR metadata and latest-main source audit; actual check receipt below. Planned portfolio/RAG checks distinguished from execution. |
| Understood | Decisions/limits/help disclosed; user-supplied direction separated from AI recommendations; student reflection/explanation still needs personal completion. Existing LEARNING is linked, not rewritten or fabricated. |

**Actual project checks (November 9, 2026):** `python3 studio.py setup` completed with the repository-pinned environment and Chromium. `python3 studio.py check` exited **0** on macOS / Python **3.14.3**: Black left 27 files unchanged; Pylint passed; **110 foundation/request tests passed**, **18 contracts through APP-003 passed**, and **11 real Chromium cases passed**. The first pytest selection deselected 11 browser cases; the browser selection later ran those 11 and deselected the 110 other cases. Those deselections are not skipped failures. A Starlette/httpx deprecation warning occurred and did not fail the run. Existing tests, instructor contracts and acceptance requirements were unchanged. This verifies the tested local APP-001/002/003 behavior, not RAG, hosting, complete security or student understanding. Raw local log: `/tmp/review1-check.log`; ignored receipt: `runtime/check-APP-003.json`. PR CI results are separate and must be checked on the actual published revision.

**Diff/privacy review:** documentation only; no secret values, credentials, private career reflection, invented biography, source permission, screenshots, peers, test passes or deployed URLs. Existing code/tests/contracts/workflows are outside the diff. Empty reflection prompts are kept outside the repository; no full personal reflection belongs here.

**Student review before submission:** confirm original job pages and eligibility privately; complete the private reflection in own words; review provisional direction/layout and explain why; author/approve five sources; choose professional contact and optionally supply resume/LinkedIn; supply real group project/contribution evidence; confirm budget/provider data terms and actual server constraints. These are open items, not actions completed by AI.

## Historical Canvas-ready individual Plan submission (Review 1)

Copy this section after reviewing the pending decisions. No hosted URL is required at Plan.

### 1. Individual portfolio + career research

Repository: https://github.com/kushalpatel71/my-app-studio

Portfolio/career Plan: https://github.com/kushalpatel71/my-app-studio/blob/feature/review1-plan/docs/review1/README.md#1-individual-portfolio--career-research

Changed: added three original employer records (Palantir FDE new graduate, GovWell AI Product Engineer, Datadog Software Engineering Intern), two-direction comparison, target reader, responsibility/evidence map and two layouts. AI application/product engineering and an evidence-first layout are provisional recommendations. Checked: original posting content and existing repository evidence; personal eligibility remains unconfirmed. Next: complete my private reflection, review direction/layout, and confirm contact/group-contribution links. The professional portfolio is planned, not built or hosted. Research and drafting were AI-assisted; no personal reflection or professional credentials were invented.

### 2. Individual RAG app + technical research

RAG technical Plan, source manifest and expected query/checks: https://github.com/kushalpatel71/my-app-studio/blob/feature/review1-plan/docs/review1/README.md#2-individual-rag-app--technical-research

Changed: planned the Car Builds Knowledge Assistant with five proposed owner-authored sources, retrieval comparison, vector-first architecture, import/chunk/graph sketches, source-reference workflow, five evaluation questions and hosting constraints. Checked: primary technical documentation and existing app/security boundaries; no RAG import, retrieval, embedding, generation or evaluation has run. Next: author/approve source permissions, review models/budget and audit actual server capacity before Build. Proposed stack: FastAPI, persistent Chroma, MiniLM embeddings and server-side Gemini generation, with SQLite keyword retrieval as a simpler fallback. No deployment or merge was performed; November 24 Build, December 3 release and December 10 peer review remain future work.

Actual local regression check: `python3 studio.py check` passed Black, Pylint, 110 foundation/request tests, 18 APP-003 cumulative contracts and 11 Chromium cases on November 9, 2026. Existing application behavior and instructor tests are preserved. This result does not establish RAG functionality.

Plan workflow: https://github.com/kushalpatel71/my-app-studio/issues/7

Pull request: https://github.com/kushalpatel71/my-app-studio/pull/8
