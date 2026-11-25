# Existing-server deployment runbook

The owner approved this isolated deployment on November 23, 2026.
The public hostname below was verified through trusted HTTPS and real Chromium.
Actual revision/check evidence and approved Free-tier configuration are in
`docs/review1/README.md`; this runbook records repeatable operations.
Application and individual evidence stay in `docs/review1/README.md`.

## Reviewed scope

- Existing SSH alias: `is373-server`; existing external network: `hosting-web`.
- New project/service/router: `cbp-review2`; proposed origin: `https://carbuilders.192.81.212.73.sslip.io`.
- One non-root container, one worker, 768 MiB memory cap, 0.75 CPU, no host application port. The RAG database has no network listener.
- New named volume `cbp-review2_app-data` retains accounts, sessions, metadata, vectors, limits and model cache under `/data`. This is a fresh app deployment; it does not migrate or alter any existing website/database.
- Existing Traefik's Docker provider discovers labels on `hosting-web`. Its `websecure` entrypoint already defaults to Let's Encrypt TLS. No proxy config edit or restart is needed.
- Preserve calculator, practical-prod, practical-qa, Traefik and all their volumes/routes. Never run a global prune, `down -v`, or remove an existing container.
- Real secret file: `/home/deployer/.config/cbp-review2/app.env`, mode 0600. Generate an independent APP_SECRET; never rotate it during an ordinary release. Add a Gemini key only through private server-side configuration. `RAG_PROVIDER_APPROVED=free-tier-confirmed` requires owner confirmation; it does not itself prove provider billing status. No paid API/project is enabled here.

## Preflight and release preparation

Run after the owner approves the plan. Recheck resources and existing service identities immediately before launch. Keep raw inspection output in a private recovery directory, outside GitHub.

```sh
ssh is373-server
nproc
free -m
df -h /
docker ps
docker stats --no-stream
docker network inspect hosting-web
docker compose version
```

Use a clean source checkout at `/home/deployer/cbp-review2`, pinned to the reviewed commit. Set `RELEASE_TAG` to that exact SHA. A secret file must be created privately from `app.env.example`, with a random APP_SECRET of at least 32 bytes. Do not copy local account data or secrets into the image.

```sh
cd /home/deployer/cbp-review2
export RELEASE_TAG=REVIEWED_COMMIT_SHA
docker compose -f deploy/compose.yml config --quiet
docker compose -f deploy/compose.yml build app
docker compose -f deploy/compose.yml up -d --no-deps app
docker compose -f deploy/compose.yml ps
docker compose -f deploy/compose.yml logs --tail=50 app
```

`config --quiet` validates without printing the resolved secret environment. Never publish `docker inspect` environment output.

## Import and administrative access

The public API checks the current administrator role and CSRF. Sign in as an existing app administrator, open `/rag`, then use **Import approved documents**. No path/upload is accepted. If this fresh deployment has no accounts, create a disposable owner account through the normal signup form and promote it only through a trusted server terminal:

```sh
docker compose -f deploy/compose.yml exec app python -c 'from app import database; from app.settings import Settings; assert database.set_role(Settings.load(), "OWNER_USERNAME", "admin")'
```

The terminal is a trusted administration boundary; there is no public role-changing endpoint. Replace the username explicitly. Do not put a password or API key in shell history.

For a trusted terminal bootstrap/import or repeatable retrieval evaluation:

```sh
docker compose -f deploy/compose.yml exec app python -c 'from app.rag_store import RagStore; from app.settings import Settings; s=RagStore(str(Settings.load().database)+".rag"); print(s.ingest())'
```

## Verify and restart

```sh
docker compose -f deploy/compose.yml ps
docker compose -f deploy/compose.yml exec app python -c 'from app.rag_store import RagStore; from app.settings import Settings; print(RagStore(str(Settings.load().database)+".rag").stats())'
curl --fail --show-error https://carbuilders.192.81.212.73.sslip.io/health
curl --fail --show-error https://carbuilders.192.81.212.73.sslip.io/portfolio
curl --fail --show-error https://carbuilders.192.81.212.73.sslip.io/rag
curl --fail --show-error https://calc.192.81.212.73.sslip.io/health
docker compose -f deploy/compose.yml restart app
```

Recheck health, source/chunk counts, login/session behavior, semantic retrieval, all existing websites and their container start times after restart. In a real browser: Portfolio → RAG case study → Ask → inspect retrieved IDs → generated answer → open cited passage. A 200 HTML page or simulated provider does not establish a real hosted RAG journey. Without a key, supported questions must show a clear 503 generation-unavailable response with retrieval trace.

## Backup and rollback

Before updates, stop **only the new app**, then export its entire named volume consistently (SQLite + Chroma + model cache). Keep archives private and copy them off-host. Test restore into a separate volume before calling backups verified. Initial deployment has no prior app data; take a first backup after import and verify its checksum off-host.

```sh
export CBP_BACKUP_DIR=/home/deployer/.config/cbp-review2/backups
mkdir -p "$CBP_BACKUP_DIR"
chmod 700 "$CBP_BACKUP_DIR"
umask 077
docker compose -f deploy/compose.yml stop app
# Restart the app even if a later command fails during this maintenance shell.
trap 'docker compose -f deploy/compose.yml start app' EXIT
docker run --rm --network none --read-only --cap-drop ALL --user 10001:10001 \
  -v cbp-review2_app-data:/source:ro --entrypoint tar \
  cbp-review2:$RELEASE_TAG -czf - -C /source . > "$CBP_BACKUP_DIR/app-data.tar.gz"
sha256sum "$CBP_BACKUP_DIR/app-data.tar.gz"
docker compose -f deploy/compose.yml restart app
trap - EXIT
```

For rollback, preserve the volume and select the previously verified source commit/image. The current schema changes are additive; before future incompatible migrations, design and verify a data rollback separately.

```sh
# In the source checkout, select the previously verified release first.
export RELEASE_TAG=PREVIOUS_VERIFIED_COMMIT_SHA
docker compose -f deploy/compose.yml up -d --no-deps --no-build app
```

For a failed **initial** launch, stop only `cbp-review2`'s app service. Keep its volume and diagnostics; existing sites remain routed by their original labels. No rollback or backup restoration has been executed merely by writing this runbook.

## Review 3 release plan — approval required, not executed

The Review 2 approval does **not** authorize this release. Current live image is
`cbp-review2:517b03c947c4fb0e14947fbda98fab11b850a267`; it remains healthy.
Review 3 changes application code only: derived source locations without schema
or chunk-ID changes, structured generation/controlled errors, and optional exact-IP
proxy identity. The corpus, model, dependencies, routes, volume, network, TLS and
resource limits remain the same. No shared Traefik edit is proposed.

Before approval: finish the PR checks and inspect the diff. After approval:

1. Capture safe service identities/start times, health, volume names and proxy
   hashes into private recovery storage. Validate capacity and existing HTTPS sites.
2. Keep the current image as rollback. Make a consistent private backup using the
   app-only stop/export/start commands above; checksum/copy off-host. Preserve the
   existing private env file and signer unchanged. Never print resolved Compose
   environment or `docker inspect` environment values.
3. Fetch the approved commit in `/home/deployer/cbp-review2` and select it. Set
   `RELEASE_TAG` to its full SHA. Validate `docker compose -f deploy/compose.yml
   config --quiet`, build **only** app, then `up -d --no-deps app`.
4. Proxy identity is disabled by default. To enable it for the approved release,
   first verify Traefik's actual `hosting-web` address and sanitized/appended XFF
   behavior, and that forwarded-header insecure/trusted-source/not-append settings
   have not changed. The observed proxy IP on November 25 was `172.18.0.4`.
   Only then set the **nonsecret shell variable** `RAG_TRUSTED_PROXY_IPS` to that
   exact verified address before Compose `up`. Do not trust the Docker subnet or
   arbitrary incoming headers. If that proof is unavailable, leave it empty and
   retain the conservative shared limit. No live proxy-aware result is claimed yet.
5. Wait for Docker health, then check original HTTPS sites and the full portfolio
   → case study → RAG → actual Gemini answer → source journey. Check five/18,
   old citation links, location spans, role/CSRF denials and safe provider errors.
   Verify session/data persistence with an app-only restart **within the approval**.
6. If release checks fail, set `RELEASE_TAG` to the retained prior image and
   `up -d --no-deps --no-build app`. Keep the same volume and secret. The isolated
   November 23 backup compatibility check confirmed old and new code can read
   that snapshot; it does not guarantee every future state. Do not restore a live
   backup or change other services without separate approval.

Repeat local retrieval evaluation (no paid/provider calls):

```sh
python scripts/check_rag_release.py --index /tmp/review3-eval --output /tmp/review3-retrieval.json
```

An explicit `--hosted-origin https://carbuilders.192.81.212.73.sslip.io` makes at
most eight questions, at least 13 seconds apart; record the **actual deployed**
revision separately from the evaluator revision. Do not run this repeatedly to
bypass daily limits. Raw receipts belong outside private backup/log directories.

Compose syntax was validated locally with `RELEASE_TAG=review3-local docker
compose -f deploy/compose.yml config --no-env-resolution --quiet`, without reading
secrets. Docker Desktop could not launch locally (missing app executable); image
build/startup/persistent restart verification runs in the dedicated GitHub CI job.
These local/CI checks do not establish an updated production release.

## Review 3 approved release — operational note

The owner explicitly approved commit `05f8da7bc6ffc6ff3470a53fa9dbba98cb4011d4`
on November 25. Production receipts and final status are in the existing individual
record; PR merge and Issue #11 closure remain separately unauthorized.

The first launch failed because the private release helper's `umask 077` propagated
into public Git checkout files. Docker copied root-owned mode-0600 application
source, which UID 10001 could not import. The health gate restored the prior image
without restoring/deleting the volume or changing secrets. Only public tracked
source-file/directory permissions were normalized; the same approved commit was
rebuilt. Before recreating production, an isolated container using UID 10001,
disposable tmpfs storage and no live credentials passed startup/routes/access denial.

For future releases, keep private backup/env/receipt creation under `umask 077`,
but use `umask 022` for public source checkout or explicitly verify its Git-tracked
public file modes before building. Never recursively chmod private runtime data,
`.git` credentials or server environment files. Run the isolated non-root startup
probe before moving traffic. A Git SHA and passing CI do not verify server build-context
permissions. Retain failed-attempt and downtime receipts; do not relabel a rollback
as first-attempt success.
