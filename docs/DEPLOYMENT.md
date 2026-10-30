# Deployment guide

## Supabase PostgreSQL
Create a Supabase project and copy its PostgreSQL connection string from database connection settings. Store it as Render's DATABASE_URL secret; never commit it. Use SSL and a connection method appropriate for Render and Supabase limits. Before production launch, add and apply reviewed database migrations; this starter creates tables automatically only in development and test environments.

## Render API
Import this repository as a Render Blueprint or create a Python web service with root directory backend. Build command: pip install -r requirements.txt. Start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT. Set APP_ENV=production, DATABASE_URL to the Supabase PostgreSQL connection string, and CORS_ORIGINS to your exact Vercel origin. Verify /api/v1/health and /api/v1/health/ready.

## Vercel frontend
Import the repository, set root directory to frontend, framework to Vite, build command to npm run build, and output directory to dist. Set VITE_API_BASE_URL to the deployed Render URL ending in /api/v1. Redeploy after changing environment variables.

## Before production
This is an initial working foundation, not a completed production business platform. Add authentication and role-based authorization before exposing admin data, rate limiting and spam protection for public forms, email delivery if needed, Alembic migrations, privacy/legal content, backups, and a security review. The admin enquiries endpoint is intentionally disabled.
