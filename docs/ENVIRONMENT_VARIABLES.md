# Environment variables

Never commit real secrets. Example files contain safe local defaults.

## Frontend
VITE_API_BASE_URL is a public browser setting, not a secret. Local value: http://localhost:8000/api/v1. In Vercel, set it to the deployed Render URL ending in /api/v1. Redeploy after changing it.

## Backend
APP_ENV selects development or production behavior. DATABASE_URL is the local SQLite URL or production Supabase PostgreSQL connection string. CORS_ORIGINS is a comma-separated list of exact allowed frontend origins. Configure production values in Render's environment settings. Do not expose database credentials in VITE_* variables.
