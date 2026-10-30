# Security status and launch checklist

## Implemented
- Admin API endpoints require a signed, expiring bearer token; no admin account is hard-coded.
- Passwords are verified against an Argon2 hash configured through environment variables.
- Admin authentication fails closed if configuration is missing or incomplete.
- Public CORS origins are explicit; the admin token is not stored in a cookie.
- Admin enquiry list is capped at 250 records per request and status updates use a fixed allow-list.

## Required before production launch
- Configure `ADMIN_EMAIL`, `ADMIN_PASSWORD_HASH`, and a random `JWT_SECRET` of at least 32 bytes in Render. Never commit real values.
- Generate the Argon2 hash locally with the command in `backend/.env.example`. Use a unique, strong admin password and keep the original password in a password manager.
- Restrict `CORS_ORIGINS` to the exact Vercel production origin (and any intentionally enabled preview origin).
- Add login rate limiting and monitoring before public launch.
- Configure Supabase backups/retention and database migrations (for example, Alembic) before schema changes in production.
- Review privacy and legal pages before accepting real customer submissions.
- The browser admin keeps the access token in session storage for the current tab. Treat XSS prevention as essential; tokens expire quickly.
- Do not collect passwords or unnecessary sensitive information in public forms.
