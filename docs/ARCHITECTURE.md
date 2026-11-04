# Architecture

- frontend/: React + Vite website with responsive CSS and React Router.
- backend/: FastAPI REST API, SQLAlchemy ORM, and Pydantic validation.
- Local database: SQLite by default.
- Production database: Supabase PostgreSQL through DATABASE_URL.
- render.yaml: Render blueprint.
- frontend/vercel.json: SPA route fallback.
- .github/workflows/ci.yml: build and test checks.

Public contact submissions are validated and persisted. The admin workspace is protected by bearer-token authentication: it lists and updates customer enquiries, manages the public service catalog, and edits the shared website settings. It is not yet a full ticketing system or CMS.
