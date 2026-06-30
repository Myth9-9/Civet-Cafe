# Deployment Guide

## Architecture

| Service | Platform | Notes |
|---------|----------|-------|
| Frontend | Vercel | React SPA via Vite |
| Backend | Railway | FastAPI via Uvicorn |
| Database | Supabase | PostgreSQL 16 |
| CI/CD | GitHub Actions | Lint, test, deploy on main push |

## Prerequisites

- GitHub repository with `main` and `develop` branches
- [Vercel](https://vercel.com) account (Hobby or Pro)
- [Railway](https://railway.app) account (Hobby or Pro)
- [Supabase](https://supabase.com) account (Free tier per project)

## 1. Supabase — Create Project Per Environment

Create **three** Supabase projects:

| Environment | Suggested Name | Supabase Project Ref |
|-------------|---------------|---------------------|
| Development | `civet-pos-dev` | From project settings |
| Staging | `civet-pos-staging` | From project settings |
| Production | `civet-pos-prod` | From project settings |

For each project:

1. Go to **Project Settings > Database** and copy the connection string (URI format).
2. Go to **Project Settings > API** and copy:
   - `Project URL` → `SUPABASE_URL`
   - `anon public` key → `SUPABASE_ANON_KEY`
   - `service_role` key → `SUPABASE_SERVICE_ROLE_KEY`
3. Under **Authentication > Settings**, confirm `JWT expiry` defaults are fine.

## 2. Database — Run Migrations

After each Supabase project is created, run Alembic migrations:

```powershell
# Development
$env:DATABASE_URL = "postgresql+psycopg://postgres:password@db.<ref>.supabase.co:5432/postgres"
alembic upgrade head

# Seed RBAC roles, permissions, and default admin
python scripts/seed.py
```

Repeat for staging and production with their respective connection strings.

## 3. Backend — Railway

### 3.1 Install Railway CLI

```powershell
npm install -g @railway/cli
railway login
```

### 3.2 Create Railway Projects

```powershell
railway init --name civet-cafe-pos-api          # production
railway init --name civet-cafe-pos-api-staging  # staging
```

### 3.3 Configure Environment Variables

Set the following variables in each Railway project dashboard (or via CLI):

| Variable | Description |
|----------|-------------|
| `APP_NAME` | Display name for the API |
| `ENVIRONMENT` | `development`, `staging`, or `production` |
| `API_V1_PREFIX` | `/api/v1` |
| `BACKEND_CORS_ORIGINS` | Comma-separated frontend URLs |
| `SUPABASE_URL` | From Supabase project settings |
| `SUPABASE_ANON_KEY` | From Supabase project settings |
| `SUPABASE_SERVICE_ROLE_KEY` | From Supabase project settings |
| `DATABASE_URL` | Full pg URI (with `postgresql+psycopg://`) |
| `JWT_SECRET_KEY` | Random 64-char hex string |
| `JWT_ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `15` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` |

**Example for production:**

```powershell
$jwtKey = -join (1..64 | ForEach-Object { '{0:x}' -f (Get-Random -Max 16) })
railway --service civet-cafe-pos-api env set ENVIRONMENT=production
railway --service civet-cafe-pos-api env set BACKEND_CORS_ORIGINS=https://civet-cafe-pos.vercel.app
railway --service civet-cafe-pos-api env set DATABASE_URL=postgresql+psycopg://...
railway --service civet-cafe-pos-api env set JWT_SECRET_KEY=$jwtKey
```

### 3.4 Deploy

```powershell
railway --service civet-cafe-pos-api up
```

Railway reads `Procfile` and `railway.json` automatically. The app starts via:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT --forwarded-allow-ips '*'
```

### 3.5 Health Check

Verify deployment:

```powershell
Invoke-RestMethod -Uri https://<railway-url>/health
# {"status":"healthy"}
```

## 4. Frontend — Vercel

### 4.1 Install Vercel CLI (optional)

```powershell
npm install -g vercel
vercel login
```

### 4.2 Create Vercel Projects

```powershell
vercel --prod --name civet-cafe-pos            # production
vercel --prod --name civet-cafe-pos-staging     # staging
```

### 4.3 Configure Environment Variables

Set these in each Vercel project dashboard (Settings > Environment Variables):

| Variable | Description |
|----------|-------------|
| `VITE_APP_NAME` | App display name |
| `VITE_API_BASE_URL` | Railway backend URL + `/api/v1` |
| `VITE_SUPABASE_URL` | From Supabase project settings |
| `VITE_SUPABASE_ANON_KEY` | From Supabase project settings |

### 4.4 Deploy

```powershell
vercel --prod
```

Or push to `main` — the GitHub Action will trigger automatically (see CI/CD below).

## 5. GitHub Actions — CI/CD

Workflows are located in `.github/workflows/`:

| Workflow | Trigger | Actions |
|----------|---------|---------|
| `backend.yml` | Push to `main` | ruff lint → mypy type check → pytest → Railway deploy |
| `frontend.yml` | Push to `main` | eslint lint → vitest test → vite build → Vercel deploy |
| `migrations.yml` | Manual (workflow_dispatch) | Alembic upgrade head on any environment |

### 5.1 Required GitHub Secrets

| Secret | Used By | Value |
|--------|---------|-------|
| `RAILWAY_TOKEN` | `backend.yml` | Railway CLI token (Settings > Tokens) |
| `RAILWAY_PROJECT_ID` | `backend.yml` | Railway production project ID |
| `RAILWAY_STAGING_PROJECT_ID` | `backend.yml` | Railway staging project ID |
| `VERCEL_TOKEN` | `frontend.yml` | Vercel access token (Account > Settings > Tokens) |
| `VERCEL_ORG_ID` | `frontend.yml` | Vercel team ID (from `vercel whoami`) |
| `VERCEL_PROJECT_ID` | `frontend.yml` | Vercel production project ID |
| `VERCEL_STAGING_PROJECT_ID` | `frontend.yml` | Vercel staging project ID |
| `SUPABASE_SERVICE_ROLE_KEY` | `migrations.yml` | Supabase service_role key |

## 6. Environments Summary

| Environment | Frontend URL | Backend URL | Supabase Project |
|-------------|-------------|-------------|-----------------|
| Development | `http://localhost:5173` | `http://localhost:8000` | `civet-pos-dev` |
| Staging | `https://staging-civet-cafe-pos.vercel.app` | `https://civet-cafe-pos-api-staging.up.railway.app` | `civet-pos-staging` |
| Production | `https://civet-cafe-pos.vercel.app` | `https://civet-cafe-pos-api.up.railway.app` | `civet-pos-prod` |

## 7. Useful Commands

```powershell
# Run migrations locally
$env:DATABASE_URL = "postgresql+psycopg://..."
alembic upgrade head

# Seed default data
python scripts/seed.py

# Check migration history
alembic history

# Rollback one migration
alembic downgrade -1

# View Railway logs
railway --service civet-cafe-pos-api logs

# Open Railway dashboard
railway --service civet-cafe-pos-api dashboard

# Open Vercel dashboard
vercel --prod --open
```

## 8. Troubleshooting

**Backend health check fails:**
- Confirm `DATABASE_URL` is correct and the Supabase project allows connections from Railway's IP range.
- Check Railway logs: `railway --service civet-cafe-pos-api logs`.

**CORS errors in browser:**
- Verify `BACKEND_CORS_ORIGINS` in Railway includes the exact frontend URL (protocol, domain, no trailing slash).
- Multiple origins: `http://localhost:5173,https://civet-cafe-pos.vercel.app`.

**Migrations fail:**
- Ensure the database user has schema creation privileges.
- Run `alembic upgrade head` locally against the target Supabase database first.

**Seed script fails:**
- Ensure `DATABASE_URL` is set and migrations have already run.
- Verify the admin user or roles don't already exist (script handles idempotency).
