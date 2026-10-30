# Oasis Technologies

Responsive corporate website starter for a software development and IT services company.

## Stack
- Frontend: React JSX, Vite, React Router, responsive CSS.
- Backend: Python, FastAPI, Pydantic, SQLAlchemy.
- Local database: SQLite.
- Production database: Supabase PostgreSQL via DATABASE_URL.
- Deployment: Vercel frontend, Render API, GitHub Actions CI.

## Included
- Responsive home, services, about, approach, and contact pages.
- Mobile navigation and contact form.
- FastAPI service listing and health endpoints.
- Validated contact enquiries saved to the database.
- Environment-based API and database configuration.
- Vercel SPA rewrite, Render blueprint, and backend tests.

## Run locally on Windows PowerShell

Backend:
    cd backend
    py -3.12 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Copy-Item .env.example .env
    uvicorn app.main:app --reload --port 8000

Frontend in a new terminal:
    cd frontend
    npm install
    Copy-Item .env.example .env.local
    npm run dev

Open the Vite URL printed in the terminal (normally http://localhost:5173). API docs: http://localhost:8000/docs.

Run backend tests from backend after installing dependencies with pytest -q.

## Deployment
Read docs/DEPLOYMENT.md and docs/ENVIRONMENT_VARIABLES.md. Never commit .env files or production credentials.

## Production readiness
This is an initial working foundation, not yet a complete production business-management platform. Authentication, admin role permissions, quote and ticket workflows, email delivery, upload storage, database migrations, rate limiting, and a production security review remain before launch. The admin enquiries endpoint intentionally returns 501 rather than exposing customer data without authentication.
