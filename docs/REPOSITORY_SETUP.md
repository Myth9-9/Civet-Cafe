# Repository Setup

## Module Scope

Module 1 establishes the deployable monorepo skeleton only. It does not include database schema, authentication, menu, order, billing, report, user, or settings business logic.

## Backend Structure

```text
backend/app/api       FastAPI routers
backend/app/core      configuration and cross-cutting concerns
backend/app/db        SQLAlchemy and Alembic integration
backend/app/models    database models, added with migrations in later modules
backend/app/repositories data access layer
backend/app/services  business logic layer
backend/app/schemas   Pydantic request/response models
backend/tests         pytest test suite
```

## Frontend Structure

```text
frontend/src/app         app providers
frontend/src/components  reusable UI components
frontend/src/config      environment parsing
frontend/src/features    module-specific UI and hooks
frontend/src/lib         shared API client and utilities
frontend/src/routes      React Router configuration
frontend/tests           critical component tests
```

## Rules Carried Forward

- React components are UI-only.
- API access uses Axios and React Query.
- Backend routes delegate business decisions to services.
- Services depend on repository interfaces or concrete repositories.
- Repositories are the only layer that talks to SQLAlchemy/Supabase Postgres.
- All database changes must be represented by Alembic migrations.

