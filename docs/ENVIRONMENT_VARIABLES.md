# Environment variables

Never commit real secrets. Example files contain safe local defaults.

## Frontend
- `VITE_API_BASE_URL` is a public browser setting, not a secret. Local value: `http://localhost:8000/api/v1`. In Vercel, set it to the deployed Render URL ending in `/api/v1`, then redeploy.

## Backend
- `APP_ENV`: use `production` on Render; database tables are not auto-created in production.
- `DATABASE_URL`: local SQLite URL or production Supabase PostgreSQL connection string.
- `CORS_ORIGINS`: comma-separated exact frontend origins.
- `ADMIN_EMAIL`: the one administrator login email.
- `ADMIN_PASSWORD_HASH`: Argon2 password hash; never store a plain-text password here.
- `JWT_SECRET`: random secret of at least 32 UTF-8 bytes. Keep it private and rotate it if exposed.
- `JWT_ACCESS_TOKEN_MINUTES`: short access-token lifetime; default 30 minutes.

Configure production backend values in Render environment settings. Do not expose database credentials or secrets in any `VITE_*` variable. Admin login stays disabled with HTTP 503 until credentials and a sufficiently long JWT secret are configured.
