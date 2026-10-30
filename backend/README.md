# FastAPI backend

Install Python 3.12+, create a virtual environment, install requirements, and copy .env.example to .env. The default DATABASE_URL uses local SQLite.

Run locally:
    uvicorn app.main:app --reload --port 8000

API docs: http://localhost:8000/docs
Tests: pytest -q

Set APP_ENV=production and DATABASE_URL to Supabase PostgreSQL on Render. The app intentionally creates tables automatically only in development/test. Add reviewed Alembic migrations before production. Admin data endpoints remain disabled until authentication and role-based authorization exist.
