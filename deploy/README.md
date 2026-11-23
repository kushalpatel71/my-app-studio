# Existing-server deployment runbook

This is an **approval-gated proposal**, not evidence that deployment occurred.
The public hostname below is proposed until external HTTPS verification succeeds.
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
docker compose -f deploy/compose.yml stop app
# Run from this project's host directory; keep this archive outside GitHub.
docker run --rm --network none --user 0:0 \
  -v cbp-review2_app-data:/source:ro -v "$PWD/private-backups:/backup" \
  --entrypoint tar cbp-review2:$RELEASE_TAG -czf /backup/app-data.tar.gz -C /source .
sha256sum private-backups/app-data.tar.gz
docker compose -f deploy/compose.yml start app
```

For rollback, preserve the volume and select the previously verified source commit/image. The current schema changes are additive; before future incompatible migrations, design and verify a data rollback separately.

```sh
# In the source checkout, select the previously verified release first.
export RELEASE_TAG=PREVIOUS_VERIFIED_COMMIT_SHA
docker compose -f deploy/compose.yml up -d --no-deps --no-build app
```

For a failed **initial** launch, stop only `cbp-review2`'s app service. Keep its volume and diagnostics; existing sites remain routed by their original labels. No rollback or backup restoration has been executed merely by writing this runbook.
