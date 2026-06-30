# Civet Cafe POS - BRAIN.md

> Central project memory for all developers and AI agents.

## Vision
Build a production-ready cloud POS for Civet Cafe using:
- React + TypeScript + Vite + Tailwind
- FastAPI
- Supabase PostgreSQL

## Source of Truth
- `/design/` contains the exported Stitch HTML and screenshots.
- `DESIGN.md` defines colors, typography, spacing and UI rules.
- Recreate the UI as reusable React components. Do **not** reuse exported HTML directly.

## Architecture
Frontend -> Axios -> FastAPI -> Services -> Repositories -> Supabase PostgreSQL

## Modules
- Authentication
- Dashboard
- Tables
- Menu
- Orders
- Billing
- Users
- Reports
- Settings

## Standards
- Clean Architecture
- SOLID
- RBAC
- JWT Authentication
- UUID primary keys
- Alembic migrations
- Tests for every module
- No business logic in React
- No direct frontend access to database

## Development Order
1. Repository setup
2. Database
3. Authentication
4. RBAC
5. Menu
6. Tables
7. Orders
8. Billing
9. Reports
10. Settings
11. Testing
12. Deployment
