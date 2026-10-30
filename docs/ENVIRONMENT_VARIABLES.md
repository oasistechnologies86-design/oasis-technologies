# Environment variables

Environment variables are settings stored in your computer or hosting-provider dashboard. They keep secrets out of source code. Never commit real secrets to GitHub.

## Frontend

- `VITE_API_BASE_URL`: public API address used by the browser.
- Local value: `http://localhost:8000/api/v1`.
- Vercel value: `https://YOUR-REAL-RENDER-HOST/api/v1`.

In Vercel, open the project → Settings → Environment Variables, add/update the value for the correct environment, then redeploy. This value is not a secret. Never put database credentials, JWT secrets or admin password hashes in a `VITE_*` variable.

## Backend

Set these in `backend/.env` for local development or Render's Environment settings for production.

- `APP_ENV`: `development` locally; `production` on Render.
- `DATABASE_URL`: local `sqlite:///./oasis_dev.db`; production Supabase PostgreSQL URL using `postgresql+psycopg://`.
- `CORS_ORIGINS`: comma-separated exact frontend origins, e.g. `https://your-site.vercel.app`.
- `ADMIN_EMAIL`: administrator sign-in email.
- `ADMIN_PASSWORD_HASH`: Argon2 password hash; never use the plain-text password here.
- `JWT_SECRET`: random private secret of at least 32 UTF-8 bytes.
- `JWT_ACCESS_TOKEN_MINUTES`: access-token lifetime in minutes; default `30`.

## Generate admin credentials

From the backend folder with the virtual environment activated, generate a password hash locally:

```powershell
python -c "from getpass import getpass; from pwdlib import PasswordHash; print(PasswordHash.recommended().hash(getpass('Enter new admin password: ')))"
```

Paste the printed hash into Render's `ADMIN_PASSWORD_HASH`. Use the password you typed (not the hash) when signing in. The password is hidden while typing and is not embedded in your shell command history.

Generate the JWT secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Paste the result into Render's `JWT_SECRET`. Keep it private.

## Database table setup

You do not need to run SQL manually. When the backend starts, it creates any missing tables in the configured database. This includes the enquiry table and editable website settings. The startup process runs in local development and production.

This automatic setup only creates missing tables. It does not migrate columns in existing tables. A future change to an existing table must include a reviewed, versioned database migration.

## Safe example

These are placeholders, not working values:

```dotenv
APP_ENV=production
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres
CORS_ORIGINS=https://your-site.vercel.app
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD_HASH=PASTE_GENERATED_HASH
JWT_SECRET=PASTE_GENERATED_RANDOM_SECRET
JWT_ACCESS_TOKEN_MINUTES=30
```
