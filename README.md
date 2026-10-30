# Oasis Technologies — Beginner Setup & Deployment Guide

This guide is written for someone setting up the project for the first time. Follow the steps in order. You do **not** need to write SQL or open the Supabase SQL Editor.

**Repository:** https://github.com/oasistechnologies86-design/oasis-technologies

## What this project uses

- **Frontend:** React + Vite (the website visitors see)
- **Backend:** Python + FastAPI (the API)
- **Local database:** SQLite (a file on your computer)
- **Live database:** Supabase PostgreSQL
- **Live backend/API:** Render
- **Live website:** Vercel
- **Source code and automatic checks:** GitHub

When you push changes to the `main` branch, GitHub stores them and connected Render/Vercel projects can redeploy automatically.

## Before you start

Create free accounts (if you do not already have them):

1. GitHub: https://github.com/
2. Supabase: https://supabase.com/
3. Render: https://render.com/
4. Vercel: https://vercel.com/

Install these on a Windows computer:

- Git: https://git-scm.com/downloads
- Python 3.12: https://www.python.org/downloads/
- Node.js LTS: https://nodejs.org/

After installation, open **PowerShell** and check the tools:

```powershell
git --version
py -3.12 --version
node --version
npm --version
```

If one command is not recognised, install that tool and reopen PowerShell.

---

## Part 1 — Download the project to your computer

Open PowerShell and run:

```powershell
git clone https://github.com/oasistechnologies86-design/oasis-technologies.git
cd oasis-technologies
```

You now have the project folder on your computer. The main folders are:

- `frontend` — React website
- `backend` — Python API
- `docs` — extra instructions

If you already downloaded the project previously, open PowerShell inside its folder and run `git pull origin main` to get the latest changes.

## Part 2 — Start the backend on your computer

The backend receives contact forms and talks to the database.

In PowerShell, from the project root, run these commands **one at a time**:

```powershell
cd backend
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

If PowerShell says script execution is disabled, run this in the same PowerShell window, then activate the environment again:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

For local development, the example configuration uses SQLite. You do not need a Supabase database to run the project on your computer.

Open the new `backend/.env` file in a text editor. For local work, keep these values:

```dotenv
APP_ENV=development
DATABASE_URL=sqlite:///./oasis_dev.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

Save the file. Leave the other example settings alone for now. Start the backend (you should still be inside the `backend` folder, with `.venv` active):

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Keep this window open. Visit these links in your browser:

- API status: http://127.0.0.1:8000/api/v1/health
- Database status: http://127.0.0.1:8000/api/v1/health/ready
- API documentation: http://127.0.0.1:8000/docs

The first start creates any missing local database tables automatically.

## Part 3 — Start the website on your computer

Open a **second PowerShell window** and navigate to the project folder you cloned. For example, if you saved it in Documents:

```powershell
cd $HOME\Documents\oasis-technologies
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

If you cloned it somewhere else, change the first `cd` line to your actual project folder. If the terminal is already inside the project folder, run only `cd frontend` before the remaining commands.

Open the local website URL printed in the terminal. It is usually http://localhost:5173.

Open `frontend/.env.local` and check that it contains:

```dotenv
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

**Both terminal windows must remain open** while you use the local website. To stop a server, click its terminal and press `Ctrl+C`.

## Part 4 — Create your live database (no SQL editor required)

1. Sign in at https://supabase.com/ and click **New project**.
2. Choose an organisation, enter a project name such as `oasis-technologies`, create a strong database password, and choose a region close to your users.
3. Wait until the project has finished creating.
4. Open the project's **Connect** or **Database settings** area and find the PostgreSQL connection string. Use a connection option that works for external services such as Render. If using a pooler, follow the connection details Supabase provides.
5. Copy the connection string and keep it private. It contains a password.
6. The connection URL for this project must use SQLAlchemy's `postgresql+psycopg://` scheme. If Supabase gives you a URL starting with `postgresql://`, change only the beginning to `postgresql+psycopg://`. Do not change the username, password, host, port or database name.

Example shape only — **do not copy this fake value**:

```text
postgresql+psycopg://postgres:YOUR_DATABASE_PASSWORD@YOUR_DATABASE_HOST:5432/postgres
```

You do **not** need to create tables by hand. When the API starts, the application creates any missing tables, including contact enquiries and website settings. This is done by the backend code, not the Supabase SQL Editor.

**Important database note:** automatic table creation adds tables that are missing; it does not modify or remove columns in tables that already exist. If a future software update changes the structure of an existing table, that update must include a proper database migration. Do not delete your database to fix a deployment.

## Part 5 — Deploy the backend API on Render

1. Sign in at https://dashboard.render.com/.
2. Choose **New** and then **Blueprint** (the wording can vary slightly).
3. Connect GitHub if asked. Select the repository `oasistechnologies86-design/oasis-technologies`.
4. Render should detect the root `render.yaml`. Review the service details and create/deploy the service.
5. Open the new service in Render and go to **Environment**.
6. Add or update the following variables. Replace every example value with your real value.

| Variable | Example / instructions |
| --- | --- |
| `APP_ENV` | `production` |
| `DATABASE_URL` | Your private Supabase connection URL from Part 4 |
| `CORS_ORIGINS` | Temporarily use `https://your-site.vercel.app` after you create the Vercel project; replace with its exact real URL |
| `ADMIN_EMAIL` | For example `oasistechnologies86@gmail.com` — the email you will use to sign in to the admin area |
| `ADMIN_PASSWORD_HASH` | Generate it in step 7 below |
| `JWT_SECRET` | Generate it in step 8 below |
| `JWT_ACCESS_TOKEN_MINUTES` | `30` |

7. Generate the admin password hash on your computer. Open PowerShell in the repository, activate the backend virtual environment, and make sure you are in the `backend` folder. Replace the example password with a strong unique password you can remember. The password below is only an example; **do not use it as your real password**:

```powershell
python -c "from pwdlib import PasswordHash; print(PasswordHash.recommended().hash('ChangeThisExamplePassword123!'))"
```

Copy the long hash printed by the command and paste it into Render's `ADMIN_PASSWORD_HASH` field. When signing in later, enter the original password you used in the command — not the hash. Avoid apostrophes in the password for this one-line command.

8. Generate the JWT secret. In PowerShell run:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copy the output into Render's `JWT_SECRET`. Do not share or commit it.

9. Save the environment settings and trigger a deploy if Render does not do so automatically.
10. Once deployed, copy the service's public URL. It looks similar to `https://oasis-technologies-api.onrender.com`. Your real URL may be different.
11. Test the API by adding `/api/v1/health` to that URL. For example: `https://YOUR-REAL-RENDER-HOST/api/v1/health`. You should see a small JSON response containing `"status":"ok"`.
12. Test `/api/v1/health/ready` as well. It should return `"status":"ready"` if the database connection works.

If you change `DATABASE_URL`, check it carefully for missing characters. Never put the database URL in a frontend variable or commit it to GitHub.

## Part 6 — Deploy the website on Vercel

1. Sign in at https://vercel.com/dashboard.
2. Click **Add New → Project**.
3. Import `oasistechnologies86-design/oasis-technologies` from GitHub.
4. In the project's configuration, set **Root Directory** to `frontend`.
5. Use these build settings:

   - Framework preset: **Vite**
   - Build command: `npm run build`
   - Output directory: `dist`
   - Install command: `npm install`

6. Before deploying, open **Environment Variables** and add:

   - Name: `VITE_API_BASE_URL`
   - Value: `https://YOUR-REAL-RENDER-HOST/api/v1`

   Replace `YOUR-REAL-RENDER-HOST` with the actual Render hostname copied in Part 5. Do not include a trailing slash after `api/v1`.

7. Deploy. When it finishes, open the website and copy its exact URL, for example `https://oasis-technologies.vercel.app`. Use your actual Vercel URL.

## Part 7 — Connect Vercel and Render

The backend must know which website is allowed to call it.

1. Return to Render → your API service → **Environment**.
2. Set `CORS_ORIGINS` to the exact Vercel website origin, for example:

```text
https://oasis-technologies.vercel.app
```

Do not add a page path such as `/contact`. Use only the scheme and domain. If you later connect a custom domain, add its origin too, separated by a comma.

3. Save the change and redeploy/restart the Render service.
4. If you change `VITE_API_BASE_URL` in Vercel later, redeploy the Vercel frontend too. Vite embeds this setting into the built website.

## Part 8 — Check that everything works

Do these checks in order:

- [ ] Open the live Vercel website on a computer.
- [ ] Open it on a phone or use the browser's mobile view.
- [ ] Open `https://YOUR-REAL-RENDER-HOST/api/v1/health` and confirm it says `ok`.
- [ ] Open `https://YOUR-REAL-RENDER-HOST/api/v1/health/ready` and confirm it says `ready`.
- [ ] Submit a test message using the Contact page.
- [ ] Open `/team/login` on your Vercel website and sign in with the admin email and original password used to generate the hash.
- [ ] Open `/team/enquiries` and confirm the test message appears.
- [ ] Use the Website Content editor to change a safe test value, save it, then check the public website reflects the change.
- [ ] Check the Render logs if any API request fails.

Remove test enquiries if you do not want to keep them.

## Part 9 — What happens when you update the code?

When Render and Vercel are connected to this GitHub repository and automatic deployments are enabled:

1. Make a change in your local project.
2. From the project root, run:

```powershell
git status
git add .
git commit -m "Describe the change"
git push origin main
```

3. GitHub Actions runs the automated checks.
4. Render redeploys the backend and Vercel redeploys the frontend after the push, if automatic deployments are enabled.
5. The backend creates any newly missing database tables when it starts. You do not have to manually create those tables.

A failed GitHub check or deployment is a signal to inspect the logs before assuming the update is live. Open the **Actions** tab in GitHub, the deployment in Render, or the deployment in Vercel to see the error.

## Admin workspace

- Admin login: `https://YOUR-VERCEL-HOST/team/login`
- Enquiries: `https://YOUR-VERCEL-HOST/team/enquiries`
- The admin login will not work until `ADMIN_EMAIL`, `ADMIN_PASSWORD_HASH`, and `JWT_SECRET` are configured on Render.
- The browser keeps the access token in session storage for the current tab. Sign out when finished.

The Website Content editor currently supports company name, public email, two phone numbers, footer tagline, and homepage heading/description. Phone and email links are available on the public site.

## Environment variables — quick reference

**Vercel (frontend):**

```dotenv
VITE_API_BASE_URL=https://YOUR-REAL-RENDER-HOST/api/v1
```

**Render (backend):**

```dotenv
APP_ENV=production
DATABASE_URL=postgresql+psycopg://YOUR_SUPABASE_CONNECTION_DETAILS
CORS_ORIGINS=https://YOUR-REAL-VERCEL-HOST
ADMIN_EMAIL=your-admin-email@example.com
ADMIN_PASSWORD_HASH=PASTE_THE_GENERATED_HASH_HERE
JWT_SECRET=PASTE_THE_GENERATED_RANDOM_SECRET_HERE
JWT_ACCESS_TOKEN_MINUTES=30
```

These are examples to explain the variable names, not working credentials. Set each variable in the relevant provider's dashboard. Do not paste real passwords, hashes, database URLs or JWT secrets into GitHub, public screenshots, or frontend variables.

## Common problems

- **`py` or Python not found:** install Python 3.12 and reopen PowerShell.
- **`npm` not found:** install Node.js LTS and reopen PowerShell.
- **Frontend says it cannot connect to the API:** check Vercel's `VITE_API_BASE_URL`, confirm the Render service is running, and redeploy Vercel after changing the variable.
- **Browser reports a CORS error:** set Render's `CORS_ORIGINS` to the exact Vercel origin, save, and redeploy Render.
- **Health says ok but database readiness fails:** check Render's `DATABASE_URL` and Supabase connection details.
- **Admin login shows 503:** check that all three admin variables are set on Render and that `JWT_SECRET` has at least 32 bytes.
- **Admin login says the password is wrong:** use the original password used to generate `ADMIN_PASSWORD_HASH`; do not enter the hash as the password.
- **A deployment failed:** open the deployment logs in the relevant service. Do not delete the database or change random settings to try to fix it.

## Important security and maintenance notes

- Never commit `.env`, `.env.local`, database credentials, passwords, password hashes or signing secrets.
- Keep the Supabase database password private.
- Keep the GitHub repository connected to Render and Vercel; verify automatic deployments are enabled.
- Keep backups and understand Supabase's backup/retention options before using the website for important customer enquiries.
- Automatic startup table creation handles **missing tables**. It does not migrate changes to columns in existing tables; future changes to an existing table need a reviewed, versioned migration.
- Email notifications, quotation workflows, support tickets and file uploads are not implemented yet.

## More documentation

- [Environment variables](docs/ENVIRONMENT_VARIABLES.md)
- [Deployment reference](docs/DEPLOYMENT.md)
- [Security checklist](docs/SECURITY.md)
