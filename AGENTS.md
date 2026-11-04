# Agent notes: oasis-technologies

FastAPI backend (`backend/`) + React/Vite frontend (`frontend/`). Deployed on
Render (API) and Vercel (static site).

## Commands

```bash
# backend
cd backend && python -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env            # then set JWT_SECRET, ADMIN_EMAIL, ADMIN_PASSWORD_HASH
PYTHONPATH=. .venv/bin/python -m pytest -q
PYTHONPATH=. .venv/bin/uvicorn app.main:app --port 8000

# frontend
cd frontend && npm install && npm run build
npm run dev                     # needs VITE_API_BASE_URL
```

## Gotchas

- `APP_ENV` must be `development` or `test` for the app to create tables and
  seed data; `production` expects the schema to already exist.
- `ADMIN_EMAIL` is validated as an email address. A reserved TLD such as
  `.test` is rejected, which surfaces as a confusing startup failure.
- Schema changes: `Base.metadata.create_all` only creates missing tables. It
  never adds columns to an existing table. Add any new column to
  `_apply_additive_migrations` in `app/main.py`, otherwise existing
  deployments (including the live Render database) will 500 on queries that
  select the new column.
- Seed data must go through the ORM (`_seed_services`). A raw `INSERT` skips
  SQLAlchemy column defaults and violates `NOT NULL` constraints.
- Tests: `TestClient(app)` must be used as a context manager (`with
  TestClient(app) as client:`) for the lifespan to run. Tests that skip it
  will not catch startup failures.
- Local dev with a proxied host needs `server: { allowedHosts: true }` in
  `frontend/vite.config.js`; do not commit that change.
