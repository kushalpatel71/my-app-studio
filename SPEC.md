# App Studio decisions

The durable agreement between learner and AI. Update only agreed decisions and
actual evidence; pending is a valid state. Keep explanations/help in
[LEARNING.md](LEARNING.md), not a second copy here.

## Current stage

- **Current feature:** APP-001.
- **Status:** Revised APP-001 static showcase implemented and checked locally; learner reviewed all six revised pages and chose Keep with a reason. Approved work committed/pushed; PR #2 is open and implementation CI check/windows passed. Learner PR review and merge approval pending.
- **Next step:** Verify CI on the latest PR revision after recording these links, then present PR #2 and CI results for learner review. Do not merge without separate approval.
- **Implementation marker:** `studio.json` is now `implemented_through: 1`, advanced only after the full APP-001 check passed; the default full check then passed again.

This repository owns application code. Server/proxy changes and production
deployment are outside these three local-development lessons. Prepared helpers
are reusable foundations, not evidence that unfinished routes are implemented.

## APP-001 · Branded homepage

**Scope:** make the neutral FastAPI homepage express one chosen identity with
a simple original SVG mark, coherent copy, navigation and shared style tokens.
Keep account actions honest about their unfinished state.

| Decision | Agreement |
|---|---|
| Visitor and concrete use situation | Car enthusiasts exploring build photos and comparing modification details for inspiration. |
| Reused IS117 brand, or name / promise / primary archetype | New brand: Car Builders Place.com. Promise: “Explore the builds. Discover what’s under the hood.” Primary archetype: Creator (AI suggestion adopted by learner). |
| One visible choice and visitor benefit | Photos beside labeled modification details so visitors can compare customization and find ideas for their own cars. |
| Own issue / branch / PR | [Issue #1](https://github.com/kushalpatel71/my-app-studio/issues/1); `feature/app-001-car-builders-place`; [PR #2](https://github.com/kushalpatel71/my-app-studio/pull/2), open. |

**Approved revised scope (learner request):** keep the branded homepage and featured previews;
add a separate Car Builds index, one static detail page per sample build and a
simple About page, using the existing FastAPI/template structure. Navbar links
must navigate to Home, Car Builds and About. Keep the charcoal/lime identity,
original SVG, responsive shared styles, credited photos and sample labels.
Accounts, uploads and car-build databases remain outside scope.

**Acceptance-test compatibility, inspected before implementation:**
`contracts/test_homepage.py` checks the saved brand and rendered homepage identity.
The prepared `test_current_lesson_browser_journey` additionally requires the
hero's primary `.button` to target a same-page fragment and bring it into view.
Changing Next Step to `/builds` would fail that browser assertion. Preserve
Next Step → `#builds` on Home, including keyboard focus and the three previews
required by our existing regression check. Add a distinct View All Builds link
to `/builds`; navbar links and View Details links use actual page URLs.
No instructor contract or existing assertion will be removed or weakened.

**Revised implementation spec (authorized by the learner's revision request):**
- Home `/`: retain hero/logo/tagline, Next Step and three featured previews; add View All Builds; move the longer purpose explanation to About.
- Car Builds `/builds`: render all three static sample builds with credited photos, model names, modification summaries and working View Details links. Images/model names also open their corresponding detail page.
- Build Details `/builds/skyline`, `/builds/miata`, `/builds/bmw`: show each build's existing representative photo, example specification overview and all four modification categories. Clearly distinguish illustrative concepts from verified pictured-car specifications; return 404 for an unknown slug.
- About `/about`: explain the enthusiast/Creator purpose and current static sample status without invented claims.
- Reuse the shared template, static brand data and responsive CSS. Use Home, Car Builds and About links with current-page indication, unique page titles/headings and keyboard focus styles.
- Add tests for real navigation, all details pages, direct requests, unknown builds, photo loading and narrow layouts. Preserve existing tests. Rerun full APP-001 and default checks at marker 1; do not advance to APP-002.

**Keep when:** the agreed identity is visible and usable at desktop/narrow widths;
full foundation + APP-001 checks pass; AI review and the learner's actual check
interpretation/browser observation/keep reason are recorded; reviewed evidence
and verified GitHub state are linked below.

## APP-002 · Signup, login and logout

**Scope:** add browser forms and REST behavior for member signup, login, a private
dashboard and logout backed by SQLite. Reuse the prepared password/JWT/CSRF/session
helpers; keep data local. New accounts cannot choose their role.

| Decision | Agreement |
|---|---|
| Expected public/private behavior and account flow | Pending |
| Valid and rejected cases to demonstrate | Pending |
| Own issue / branch / PR | Pending |

**Keep when:** the agreed forms/API work; duplicate/invalid signup and wrong
credentials are rejected; passwords are hashed; authentication uses validated,
expiring JWTs with protected cookies and CSRF; private requests require a live
session and logout revokes it. Full cumulative checks, AI review, actual learner
contributions and GitHub state are recorded. This is not a production-security certification.

## APP-003 · Server-enforced roles

**Scope:** enforce a small member/admin boundary in the API and browser. Assign
roles only through the trusted local terminal command; use current server-side
permissions, including for an existing session after a role change.

| Visitor | Homepage | Member area | Admin area/API |
|---|---|---|---|
| Anonymous | Allowed | Login required | Login required |
| Member | Allowed | Allowed | Forbidden |
| Admin | Allowed | Allowed | Allowed |

| Decision | Agreement |
|---|---|
| Intended admin-only result | Pending |
| Actual allowed/denied request evidence | Pending |
| Own issue / branch / PR | Pending |

**Keep when:** a direct request cannot bypass the role boundary, role changes
take effect as specified, new signup remains member-only, and full cumulative
checks plus AI review pass. Link the learner's actual interpretation/observation,
reviewed record and verified GitHub result. Hidden navigation alone is insufficient.

## Evidence

Link actual files/checks and the student's own issues/PRs. No fabricated URLs,
customer research or claims that a timestamp proves learning.

| Feature | Files / own issue / PR | Actual checks and learner observations | Kept / GitHub state |
|---|---|---|---|
| APP-001 | [Issue #1](https://github.com/kushalpatel71/my-app-studio/issues/1); `feature/app-001-car-builders-place`; static showcase router, templates, brand data, shared CSS/SVG/photos and route/browser tests. [PR #2](https://github.com/kushalpatel71/my-app-studio/pull/2), open. | Revised full explicit/default checks: Black/Pylint, 104 foundation/route tests, 2 homepage contracts, 7 Chromium cases passed. Learner interpretation recorded; learner inspected all six revised pages, preferred actual page navigation/detail pages and reported responsive adjustment in a narrower window. | Learner requested separate pages before Keep; revised implementation checked locally. Learner chose Keep: separate pages make navigation, comparison and finding modification details easier. Learner approved the summary and Keep workflow; committed/pushed and PR #2 opened. Implementation CI check/windows passed; final-revision CI and learner PR review precede merge. Merge is explicitly not authorized. |
| APP-002 | Pending | Unfinished; explicit contracts not yet passed | Pending |
| APP-003 | Pending | Unfinished; explicit contracts not yet passed | Pending |

### APP-001 local implementation and check evidence

**Recorded Keep decision:** the learner wants to keep the multi-page version because
Home, Car Builds, individual Build Details and About make the site easier to
navigate and help enthusiasts compare modifications without one long scroll.
The learner approved summary accuracy/publication and authorized commit/push/PR on
2026-11-02. Separate PR/CI review and approval remain required before merge.

**Implementation and test links:** [static routes](app/showcase.py),
[brand and sample data](app/brand.json), [Home](app/templates/home.html),
[Car Builds](app/templates/builds.html), [Build Details](app/templates/build_detail.html),
[About](app/templates/about.html), [shared base](app/templates/base.html),
[shared cards](app/templates/_build_cards.html), [styles](app/static/site.css),
[original SVG](app/static/logo.svg), [photo credits](app/static/photos/credits.json),
[route tests](tests/test_showcase.py), [Chromium tests](tests/browser/test_browser.py),
[unchanged homepage contracts](contracts/test_homepage.py),
[CI workflow](.github/workflows/check.yml),
[actual issue](https://github.com/kushalpatel71/my-app-studio/issues/1).
**GitHub evidence:** [PR #2](https://github.com/kushalpatel71/my-app-studio/pull/2) (open, `Closes #1`),
[implementation commit `9ecd9f6`](https://github.com/kushalpatel71/my-app-studio/commit/9ecd9f6c65f2a1230dcdddce17c9fd4f4b7135aa),
[implementation CI run](https://github.com/kushalpatel71/my-app-studio/actions/runs/41519046897) — `check` and `windows` both completed successfully.
Linux CI passed 104 foundation/route tests, 2 contracts and 7 Chromium cases.
Windows CI passed 102 foundation/route tests, 2 contracts and 7 Chromium cases,
with 2 existing POSIX-only tests skipped by their platform markers.
This evidence update changes documentation only; verify the latest PR revision
before requesting learner merge approval. Issue #1 remains open until the approved merge.

- The earlier single-page version passed Black/Pylint, 98 foundation tests, 2 contracts and 5 Chromium cases. The learner interpreted its Next Step check and reviewed that version, then explicitly requested separate pages before commit/push.
- Revised implementation: `app/showcase.py` adds `/builds`, `/builds/{slug}` and `/about`; `app/main.py` registers the router. Static data remains in `app/brand.json`, including clearly labeled concept specifications. No car-build database, authentication or upload feature was added.
- Shared `base.html`, `_build_cards.html`, `home.html`, `builds.html`, `build_detail.html` and `about.html` render Home, the build index, all three details pages and About. Car images/model names and View Details link to detail URLs. Navbar links are actual page URLs with current-page indication. Next Step remains `#builds`; View All Builds opens `/builds`.
- `app/static/logo.svg` remains the original car/garage/bolt mark. Shared CSS preserves the charcoal/lime palette, visible focus, reduced-motion handling and responsive layouts. Three local JPEGs and `app/static/photos/credits.json` retain photographer/source/license links. Each details page uses the corresponding existing representative photo; no additional photo angles or measured performance claims are invented.
- Revised checks on 2026-11-02: `python3 studio.py check --lesson APP-001` and `python3 studio.py check` both exited 0: Black, Pylint, **104 foundation/route tests, 2 homepage contracts and 7 actual Chromium cases**. Marker remains 1. Existing FastAPI/httpx deprecation warning did not fail either run.
- Instructor contracts and existing browser assertions are unchanged. `tests/test_showcase.py` adds direct public/detail-route checks and unknown-build 404 cases. The added `test_separate_showcase_page_navigation` checks real links at 1440/390px, each detail page, keyboard Enter on View Details, loaded photos, modification content, Back to Car Builds, About/Home navigation, no overflow and preserved Next Step. The earlier gallery/focus test still runs at 1440/768/390px.
- AI browser review: all six live pages returned 200 with loaded photos, no horizontal overflow at 1440/390/320px, and no browser script errors. Desktop/narrow screenshots were inspected for the gallery, detail, About and revised Home layouts; detail specifications/modifications stack on narrow screens. These are AI observations. The learner separately reported checking all six pages, easier Home/Car Builds/About navigation, working detail-page buttons, responsive adjustment in a narrower window and a preference for this multi-page version.
- Learner approved summary publication; implementation commit and both implementation CI jobs are verified above. Latest PR revision and learner review must be verified before merge. Local full-check receipt is ignored at `runtime/check-APP-001.json`. Credentials, keys, environments and local SQLite files remain outside tracked changes.

The instructor's reference branches show possible implementations. They do not
establish this repository's completion or the learner's own reasoning.
