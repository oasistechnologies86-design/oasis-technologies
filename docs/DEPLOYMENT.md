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


## Editable public website settings

The admin workspace at `/team/enquiries` includes a Website Content editor for the company name, public email, two phone numbers, footer tagline and homepage heading/description. The public frontend reads these values from `GET /api/v1/site-settings`; only authenticated admins can read the protected settings endpoint or save updates through `PUT /api/v1/admin/site-settings`.

Before production deployment, open the Supabase SQL Editor and review/run `backend/sql/20261030_site_settings.sql` once. This creates and seeds the `site_settings` table. Local development creates the table automatically through SQLAlchemy.

The public header stays visible while scrolling. The contact page includes clickable phone links, email, and WhatsApp. A four-step visitor tour appears on first visit; visitors can dismiss it and reopen it with the Help button. Theme selection persists in the browser.
