# Oasis Technologies

Responsive website and API for Oasis Technologies, a software development and IT services company.

**Stack:** React JSX + Vite frontend, Python + FastAPI backend, SQLite locally, Supabase PostgreSQL in production, GitHub Actions, Vercel and Render.

## Features

- Responsive Home, Services, About, Approach and Contact pages.
- Sticky navigation, light/dark theme toggle, and a dismissible step-by-step visitor tour.
- Click-to-call phone numbers, email links and WhatsApp contact action.
- Admin-editable public company name, contact details, tagline and homepage hero copy, shared across public pages.
- Contact enquiries validated and saved by the API.
- Private admin sign-in and enquiry dashboard at \`/team/login\` and \`/team/enquiries\`.
- API health checks and service listing.
- GitHub Actions workflow for frontend build and backend tests.

## 1. Install prerequisites

Install:
- Git: https://git-scm.com/downloads
- Python 3.12: https://www.python.org/downloads/
- Node.js 22 LTS (includes npm): https://nodejs.org/

On Windows PowerShell, verify:

\`\`\`powershell
git --version
py -3.12 --version
node --version
npm --version
\`\`\`

## 2. Clone the repository

\`\`\`powershell
git clone https://github.com/oasistechnologies86-design/oasis-technologies.git
cd oasis-technologies
\`\`\`

For an existing clone, update it with \`git pull origin main\`.

## 3. Run the backend locally (Terminal 1)

From the repository root:

\`\`\`powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
\`\`\`

If PowerShell blocks activation, allow it only for the current terminal and retry:

\`\`\`powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
\`\`\`

The default backend configuration uses local SQLite. Development mode creates the local tables automatically. Leave this terminal open.

Check:
- API health: http://127.0.0.1:8000/api/v1/health
- Database readiness: http://127.0.0.1:8000/api/v1/health/ready
- Interactive API docs: http://127.0.0.1:8000/docs

## 4. Run the frontend locally (Terminal 2)

Open a second terminal at the repository root:

\`\`\`powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
\`\`\`

Open the URL Vite prints, normally http://localhost:5173. The local \`frontend/.env.local\` should contain:

\`\`\`dotenv
VITE_API_BASE_URL=http://localhost:8000/api/v1
\`\`\`

After editing frontend environment variables, restart the Vite server. To test locally, open the website, submit a test contact form and verify the API is responding.

## 5. Run tests and build

Backend tests (from a terminal with the backend virtual environment activated):

\`\`\`powershell
cd backend
pytest -q
\`\`\`

Frontend production build:

\`\`\`powershell
cd frontend
npm run build
\`\`\`

The built website is output to \`frontend/dist\`. GitHub Actions runs both the frontend build and backend tests for pushes and pull requests to \`main\`. Review results at https://github.com/oasistechnologies86-design/oasis-technologies/actions before release.

## 6. Push your changes to GitHub

From the project root:

\`\`\`powershell
git status
git add .
git commit -m "Describe your change"
git push origin main
\`\`\`

Never commit \`.env\`, \`.env.local\`, database URLs, passwords, hashes or signing secrets. They should remain in local environment files or deployment-provider settings.

## 7. Deploy the live application

The live architecture is GitHub (source) + Supabase (database) + Render (API) + Vercel (website). Create accounts if needed at https://supabase.com/, https://render.com/ and https://vercel.com/.

### A. Create the production database on Supabase

1. Create a Supabase project and store the database password securely.
2. Open the database connection settings and copy a PostgreSQL connection string suitable for your Render service. Follow Supabase's recommendation for direct or pooler connections for your network.
3. Keep this URL private. Never put it in frontend code, GitHub files, or a \`VITE_*\` variable.
4. This backend installs the \`psycopg\` driver. For SQLAlchemy, use a connection URL whose scheme is \`postgresql+psycopg://\`. If Supabase gives you \`postgresql://\`, change only that scheme to \`postgresql+psycopg://\`; preserve the remaining URL and parameters.
5. **Important:** the app creates tables automatically only in development/test mode, not in production. Before the live contact form can save enquiries, create the production schema with a reviewed migration or controlled one-time schema setup. Alembic migrations are not included yet. A successful health check alone does not prove the enquiries table exists. This release adds the `site_settings` table too; in Supabase SQL Editor, review and run `backend/sql/20261030_site_settings.sql` once before deploying the API. It creates the settings table and seeds the public contact details supplied by the owner.

### B. Deploy the Python API on Render

1. In https://dashboard.render.com/, select **New → Blueprint** and connect this GitHub repository. Render can use the root-level \`render.yaml\`. Alternatively, create a Python web service manually.
2. For manual setup, configure:
   - Root directory: \`backend\`
   - Build command: \`pip install -r requirements.txt\`
   - Start command: \`uvicorn app.main:app --host 0.0.0.0 --port $PORT\`
   - Health-check path: \`/api/v1/health\`
3. In Render's Environment settings, configure:

   | Variable | Value |
   | --- | --- |
   | \`APP_ENV\` | \`production\` |
   | \`DATABASE_URL\` | Private Supabase URL using \`postgresql+psycopg://\` |
   | \`CORS_ORIGINS\` | Exact Vercel origin, e.g. \`https://your-project.vercel.app\` |
   | \`ADMIN_EMAIL\` | Your admin login email |
   | \`ADMIN_PASSWORD_HASH\` | Argon2 hash of your admin password |
   | \`JWT_SECRET\` | Random private secret, at least 32 bytes |
   | \`JWT_ACCESS_TOKEN_MINUTES\` | \`30\` (optional default) |

4. Generate an Argon2 password hash locally. Run this from the backend virtual environment; replace the placeholder with a strong unique password. This example uses a quoted string, so avoid apostrophes in the password or use a local script that reads it securely.

   \`\`\`powershell
   python -c "from pwdlib import PasswordHash; print(PasswordHash.recommended().hash('REPLACE_WITH_YOUR_LONG_UNIQUE_PASSWORD'))"
   \`\`\`

   Paste the resulting hash into Render's \`ADMIN_PASSWORD_HASH\` setting. Do not commit it or your plain-text password.
5. Generate a JWT signing secret locally:

   \`\`\`powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   \`\`\`

   Paste the output into Render's \`JWT_SECRET\`. Keep it private.
6. Deploy the service and copy its public HTTPS URL, for example \`https://your-api.onrender.com\`.
7. Check \`https://YOUR-RENDER-HOST/api/v1/health\` and \`https://YOUR-RENDER-HOST/api/v1/health/ready\`. Apply the production database schema before testing contact submission.

### C. Deploy the React website on Vercel

1. Open https://vercel.com/dashboard and choose **Add New → Project**. Import this GitHub repository.
2. Set **Root Directory** to \`frontend\`. Use the Vite framework preset, build command \`npm run build\`, output directory \`dist\`, and install command \`npm install\`.
3. In Vercel project settings, add this environment variable for Production:

   \`\`\`dotenv
   VITE_API_BASE_URL=https://YOUR-RENDER-HOST/api/v1
   \`\`\`

   Replace the example host with your actual Render API hostname. This value is public; never place secrets here.
4. Deploy the frontend. Copy its exact HTTPS origin (scheme + hostname, no path).
5. Return to Render and set \`CORS_ORIGINS\` to that exact Vercel origin. If you use a custom domain, add that origin too. Only allow preview origins if you need them. Save and redeploy/restart the API.
6. If you change \`VITE_API_BASE_URL\`, redeploy Vercel: Vite embeds these values into the frontend build.

### D. Verify the live deployment

1. Open your Vercel website and check it on desktop and mobile.
2. Confirm the Render health and database-readiness endpoints work.
3. Submit a test contact enquiry and confirm it is saved in Supabase.
4. Visit \`https://YOUR-VERCEL-HOST/team/login\` and sign in using the email and password whose hash you configured on Render.
5. Open \`/team/enquiries\`, confirm the test enquiry appears, and check that you can change its status.
6. If anything fails, check browser developer tools, Render logs, Vercel deployment logs and GitHub Actions. Remove test customer data if appropriate.

## 8. Admin workspace

- Sign in: \`/team/login\`
- Enquiry dashboard: \`/team/enquiries\`
- Supports \`new\`, \`in_progress\` and \`resolved\` statuses; displays up to the latest 250 enquiries.
- Login intentionally stays disabled until \`ADMIN_EMAIL\`, \`ADMIN_PASSWORD_HASH\` and a \`JWT_SECRET\` of at least 32 bytes are configured.
- The browser stores the access token in session storage for the current tab. Use HTTPS in production and sign out when finished.

## 9. Environment variables

**Frontend** — \`frontend/.env.local\` locally; Vercel project settings in production:
- \`VITE_API_BASE_URL\`: API base URL ending in \`/api/v1\`. Local value: \`http://localhost:8000/api/v1\`.

**Backend** — \`backend/.env\` locally; Render Environment settings in production:
- \`APP_ENV\`: \`development\` locally; \`production\` on Render.
- \`DATABASE_URL\`: \`sqlite:///./oasis_dev.db\` locally; Supabase PostgreSQL in production.
- \`CORS_ORIGINS\`: comma-separated allowed frontend origins.
- \`ADMIN_EMAIL\`: administrator's sign-in email.
- \`ADMIN_PASSWORD_HASH\`: Argon2 hash, never a plain-text password.
- \`JWT_SECRET\`: private random secret, at least 32 bytes.
- \`JWT_ACCESS_TOKEN_MINUTES\`: token lifetime in minutes; default 30.

See also [Environment variables guide](docs/ENVIRONMENT_VARIABLES.md), [Deployment guide](docs/DEPLOYMENT.md), and [Security checklist](docs/SECURITY.md).

## 10. Troubleshooting

- **Python launcher not found:** install Python 3.12, enable the launcher/PATH options, then reopen PowerShell.
- **PowerShell blocks activation:** use the process-scoped execution policy command in Section 3.
- **Port already in use:** stop the other process or choose another port. If the API port changes, update \`VITE_API_BASE_URL\`.
- **CORS or network error:** confirm the frontend API URL is the Render host ending in \`/api/v1\`; set Render \`CORS_ORIGINS\` to the exact Vercel origin and redeploy as needed.
- **Admin login returns 503:** configure all three admin variables on Render and redeploy.
- **Database connection fails:** check Supabase credentials, network/pooler settings and the \`postgresql+psycopg://\` scheme.
- **Contact form cannot save:** ensure the production schema has been created and database readiness succeeds; a running API does not guarantee the enquiries table exists.
- **Environment change not reflected:** check that the variable is set on the correct service/environment and redeploy. Frontend variables need the \`VITE_\` prefix.

## 11. Production launch checklist

This repository is a functional starter, not yet a complete business management platform. Before accepting real customer data, complete and test production schema setup/migrations, backups and retention, login rate limiting and monitoring, privacy/legal content, and a security review. Email notifications, quotation workflows, support-ticket management and file uploads are not implemented yet.
