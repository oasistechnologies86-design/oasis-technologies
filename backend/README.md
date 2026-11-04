# FastAPI backend

Install Python 3.12+, create a virtual environment, install requirements, and copy .env.example to .env. The default DATABASE_URL uses local SQLite.

Run locally:
    uvicorn app.main:app --reload --port 8000

API docs: http://localhost:8000/docs
Tests: pytest -q

Set APP_ENV=production and DATABASE_URL to Supabase PostgreSQL on Render. Tables are created automatically when the service starts, and a small additive migration adds columns introduced by later releases to an existing database. A future change to an existing table's structure should still be accompanied by a reviewed, versioned migration (for example, Alembic). Admin data endpoints require a signed bearer token and are enabled once ADMIN_EMAIL, ADMIN_PASSWORD_HASH, and JWT_SECRET are configured.
