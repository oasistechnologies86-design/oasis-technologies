# Deployment guide

For the full beginner-friendly walkthrough, see the [root README](../README.md). It explains each provider dashboard, the exact environment variable names, sample values, testing, and redeployment.

## Architecture

- GitHub stores the source code and runs the CI checks.
- Vercel serves the React/Vite frontend from `frontend`.
- Render runs the FastAPI backend from `backend`.
- Supabase provides the production PostgreSQL database.
- Local development uses SQLite.

## Database setup — no SQL Editor required

1. Create a Supabase project and keep its database password private.
2. Copy the PostgreSQL connection URL for Render.
3. Use the SQLAlchemy URL scheme `postgresql+psycopg://`. If Supabase provides `postgresql://`, change only that scheme and keep the remaining connection details unchanged.
4. Set the URL in Render's `DATABASE_URL` environment variable. Never put it in frontend configuration or GitHub.
5. On startup, the API runs SQLAlchemy's `Base.metadata.create_all` to create missing tables in every environment, including production. This creates the contact enquiries and site settings tables without a manual SQL step.

**Schema limitation:** `create_all` is additive. It creates tables that are absent, but does not add, rename, or remove columns in a table that already exists. If a future release changes an existing table's structure, include a reviewed, versioned database migration as part of that release. Do not delete the production database to resolve deployment errors.

## Render API

Create a **Web Service manually** in Render. Do not choose Blueprint.

1. Open https://dashboard.render.com/ and click **New + → Web Service**.
2. Connect GitHub and select `oasistechnologies86-design/oasis-technologies`.
3. Enter these service settings:

- Name: `oasis-technologies-api`
- Branch: `main`
- Root directory: `backend`
- Runtime: `Python 3`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Health-check path: `/api/v1/health`

4. Click **Create Web Service**. Then open the service's **Environment** tab and add the variables below.

Set the following in Render's Environment settings:

- `APP_ENV=production`
- `DATABASE_URL`: Supabase URL using `postgresql+psycopg://`
- `CORS_ORIGINS`: exact Vercel origin, e.g. `https://your-site.vercel.app`
- `ADMIN_EMAIL`: administrator sign-in email
- `ADMIN_PASSWORD_HASH`: Argon2 hash generated locally
- `JWT_SECRET`: random secret generated locally, at least 32 bytes
- `JWT_ACCESS_TOKEN_MINUTES=30`

Never commit secret values. See [Environment variables](ENVIRONMENT_VARIABLES.md) and [Security checklist](SECURITY.md).

## Vercel frontend

Import the GitHub repository into Vercel and set:

- Root directory: `frontend`
- Build command: `npm run build`
- Output directory: `dist`
- Install command: `npm install`
- Environment variable `VITE_API_BASE_URL=https://YOUR-REAL-RENDER-HOST/api/v1`

After deploying Vercel, copy the exact website origin and set it in Render's `CORS_ORIGINS`. Redeploy Render after changing the variable. Redeploy Vercel after changing `VITE_API_BASE_URL`.

## Automatic redeployment

Enable automatic deployments from the `main` branch in both Render and Vercel. A push to `main` should trigger a frontend and backend deployment. GitHub Actions separately builds the frontend and runs backend tests. Confirm the checks and deployments succeeded before assuming a change is live.

## Verify before launch

- Open `/api/v1/health` and `/api/v1/health/ready` on the Render host.
- Submit a contact enquiry and confirm it persists.
- Sign in at `/team/login` and test the admin dashboard at `/team/enquiries`.
- Save a harmless test change in the Website Content editor and confirm the public page updates.
- Confirm CORS is limited to the expected website origins.
- Review backups/retention, login rate limiting/monitoring, privacy/legal content and security before using real customer data.

Email notifications, quotations, support tickets and file uploads are not implemented yet.

## Website settings and visitor features

The admin workspace includes a Website Content editor for the company name, public email, two phone numbers, footer tagline and homepage heading/description. Public pages read these values through `GET /api/v1/site-settings`; authenticated admins save updates through `PUT /api/v1/admin/site-settings`.

The header remains visible while scrolling. The Contact page includes clickable phone links, email and WhatsApp. A four-step visitor tour appears on first visit; visitors can dismiss it and reopen it using the Help button. Theme selection persists in the browser.
