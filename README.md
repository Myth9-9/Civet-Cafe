# Civet Cafe POS & Billing System

Production-ready cloud POS and billing system for Civet Cafe.

## Architecture

```
React -> Axios -> FastAPI routes -> Services -> Repositories -> Supabase Postgres
```

Business logic belongs in backend services. React components render UI and call API hooks only. The frontend never connects directly to Supabase or PostgreSQL.

## Repository Layout

```
backend/   FastAPI, SQLAlchemy 2.0, Alembic, pytest
frontend/  React, TypeScript, Vite, Tailwind CSS, React Query, Axios
design/    Stitch visual reference only; do not reuse exported HTML
docs/      Architecture, database, API, deployment, and project notes
```

## Prerequisites

- **Git** — clone the repository
- **Python 3.12+** — [python.org](https://python.org)
- **Node.js 22+** — [nodejs.org](https://nodejs.org)
- **PostgreSQL 16** (or a [Supabase](https://supabase.com) project) — for the database
- **PowerShell 5.1+** — already included on Windows 10/11

Verify your environment:

```powershell
python --version
node --version
npm --version
psql --version  # optional, only for local PostgreSQL
```

## 1. Clone the Repository

```powershell
git clone https://github.com/your-org/civet-pos.git
Set-Location -LiteralPath civet-pos
```

## 2. Database Setup

You need a running PostgreSQL instance. Choose one:

### Option A: Supabase (Recommended)

1. Create a free project at [supabase.com](https://supabase.com)
2. Go to **Project Settings > Database** — copy the connection string (URI format)
3. Go to **Project Settings > API** — copy `Project URL`, `anon public` key, and `service_role` key

### Option B: Local PostgreSQL

Create the database:

```powershell
psql -U postgres -c "CREATE DATABASE civet_pos_dev;"
```

## 3. Backend Setup

### 3.1 Configure Environment

```powershell
Copy-Item -Path "backend\.env.example" -Destination "backend\.env"
```

Edit `backend\.env` and fill in your database credentials:

```
DATABASE_URL=postgresql+psycopg://postgres:password@db.your-project-ref.supabase.co:5432/postgres
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
JWT_SECRET_KEY=change-this-to-a-random-64-char-string
```

### 3.2 Create Virtual Environment and Install Dependencies

```powershell
Set-Location -LiteralPath backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### 3.3 Run Database Migrations

```powershell
alembic upgrade head
```

### 3.4 Seed Default Data

```powershell
python scripts/seed.py
```

This creates:
- **Permissions** — 13 permission records (menu.read, orders.write, billing.read, etc.)
- **Roles** — `admin` (all permissions) and `cashier` (limited permissions)
- **Admin user** — `admin@civetcafe.com` (update the password or email in the script as needed)

### 3.5 Start the Backend Server

```powershell
uvicorn app.main:app --reload
```

The API is now running at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## 4. Frontend Setup

### 4.1 Configure Environment

Open a **new terminal** (keep the backend running):

```powershell
Set-Location -LiteralPath frontend
Copy-Item -Path ".env.example" -Destination ".env"
```

Edit `frontend\.env`:

```
VITE_APP_NAME="Civet Cafe POS"
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_SUPABASE_URL=https://your-project-ref.supabase.co
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

### 4.2 Install Dependencies and Start

```powershell
npm install
npm run dev
```
The frontend is now running at `http://localhost:5173`.

## 5. Running Tests

### Backend Tests

```powershell
Set-Location -LiteralPath backend
.\.venv\Scripts\Activate.ps1
pytest
```

With coverage report:

```powershell
pytest --cov=app --cov-report=term-missing
```

### Frontend Tests

```powershell
Set-Location -LiteralPath frontend
npm test
```

## 6. Lint and Type Checking

### Backend

```powershell
Set-Location -LiteralPath backend
.\.venv\Scripts\Activate.ps1
ruff check app tests scripts
mypy app scripts
```

### Frontend

```powershell
Set-Location -LiteralPath frontend
npm run lint
npm run build  # also runs TypeScript compiler
```

## 7. Database Migrations (Alembic)

Create a new migration after modifying models:

```powershell
alembic revision --autogenerate -m "description_of_change"
```

Apply pending migrations:

```powershell
alembic upgrade head
```

Rollback the last migration:

```powershell
alembic downgrade -1
```

View migration history:

```powershell
alembic history
```

## 8. Quick Reference

| Action | Command |
|--------|---------|
| Start backend | `uvicorn app.main:app --reload` (from `backend/` with venv active) |
| Start frontend | `npm run dev` (from `frontend/`) |
| Run backend tests | `pytest` (from `backend/` with venv active) |
| Run frontend tests | `npm test` (from `frontend/`) |
| Apply migrations | `alembic upgrade head` (from `backend/` with venv active) |
| Seed database | `python scripts/seed.py` (from `backend/` with venv active) |
| Lint backend | `ruff check app tests scripts` (from `backend/` with venv active) |
| Type check backend | `mypy app scripts` (from `backend/` with venv active) |

## 9. Deployment

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for deploying to Vercel (frontend), Railway (backend), and Supabase (database) across development, staging, and production environments.

## Module Build Order

1. Repository setup
2. Database schema design and Alembic migration setup
3. Authentication and dynamic RBAC
4. Menu module
5. Tables module
6. Orders module
7. Billing module
8. Reports module
9. Users and Settings modules
10. Testing pass
11. CI/CD pipeline
12. Deployment
