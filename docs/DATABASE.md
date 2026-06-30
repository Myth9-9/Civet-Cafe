# Database

All schema changes are managed through Alembic and target Supabase PostgreSQL.
SQLite is not supported for application development or tests.

## Initial Schema

- `roles`
- `permissions`
- `role_permissions`
- `users`
- `categories`
- `menu_items`
- `tables`
- `orders`
- `order_items`
- `bills`
- `payments`
- `refresh_tokens`
- `settings`
- `audit_logs`

## Invariants

- Every table has a single UUID `id` primary key.
- Every table has `created_at` and `updated_at` timestamps.
- `updated_at` is maintained by a PostgreSQL trigger.
- Soft deletes use nullable `deleted_at` on `users`, `categories`, `menu_items`, and `tables`.
- Refresh tokens are stored as hashes, rotated on use, and revoked on logout.
- Foreign keys use explicit `ON DELETE` behavior.
- Frequently queried columns have explicit indexes.
- Enums are PostgreSQL enum types, not free-form text.

## Migration Commands

```bash
cd backend
alembic upgrade head
alembic downgrade -1
```

`DATABASE_URL` must point to Supabase PostgreSQL using the SQLAlchemy psycopg driver, for example:

```text
postgresql+psycopg://postgres:<password>@<host>:5432/postgres
```
