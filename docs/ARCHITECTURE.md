# Architecture

- frontend/: React + Vite website with responsive CSS and React Router.
- backend/: FastAPI REST API, SQLAlchemy ORM, and Pydantic validation.
- Local database: SQLite by default.
- Production database: Supabase PostgreSQL through DATABASE_URL.
- render.yaml: Render blueprint.
- frontend/vercel.json: SPA route fallback.
- .github/workflows/ci.yml: build and test checks.

Public contact submissions are validated and persisted. Administrative data access remains disabled until authentication and authorization are implemented. Do not present this starter as a finished ticketing system or CMS.
