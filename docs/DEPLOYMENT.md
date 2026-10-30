# Deployment guide

The step-by-step end-to-end deployment instructions are in the root [README](../README.md), under **Deploy the live application**. This page is a concise reference.

## Architecture
- Vercel serves the React/Vite frontend from the `frontend` directory.
- Render runs the FastAPI service from the `backend` directory.
- Supabase provides PostgreSQL.
- GitHub Actions builds the frontend and runs backend tests.

## Supabase PostgreSQL
1. Create a Supabase project and copy a database connection URL suitable for Render.
2. Store the connection URL only in Render's `DATABASE_URL` environment variable.
3. Because this project installs `psycopg`, use SQLAlchemy URL scheme `postgresql+psycopg://`.
4. Create the production database schema using a reviewed migration or controlled one-time setup before accepting enquiries. Automatic table creation is limited to development/test; Alembic migrations are not included yet.

## Render API
Import the repository as a Blueprint using `render.yaml`, or create a Python web service:
- Root directory: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health check: `/api/v1/health`

Set `APP_ENV=production`, the Supabase `DATABASE_URL`, exact frontend origin(s) in `CORS_ORIGINS`, and the administrator values `ADMIN_EMAIL`, `ADMIN_PASSWORD_HASH` (Argon2), and `JWT_SECRET` (random secret at least 32 bytes). Generate credentials locally; do not commit them. See [Security checklist](SECURITY.md).

## Vercel frontend
Import the repository with root directory `frontend`, build command `npm run build`, and output directory `dist`. Set `VITE_API_BASE_URL` to the Render API origin ending in `/api/v1`. Redeploy after changing environment variables. Add the exact Vercel site origin to Render's `CORS_ORIGINS` and redeploy the API.

## Verify before launch
- Review successful GitHub Actions runs.
- Test the health and database readiness endpoints.
- Submit a contact enquiry and confirm it persists in Supabase.
- Sign in at `/team/login`, inspect `/team/enquiries`, and test status updates.
- Confirm CORS is limited to expected frontend origins.
- Finish database migrations, backups/retention, login rate limiting/monitoring, privacy/legal content, and a production security review.

Email notifications, quotations, support tickets and file uploads are not implemented yet.
