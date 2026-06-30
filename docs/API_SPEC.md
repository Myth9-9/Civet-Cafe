# API Specification

Base path: `/api/v1`

## Auth

### `POST /auth/login`

Authenticates staff credentials with Supabase Auth, verifies the mapped local POS user is active, then returns an API-issued access token and rotating refresh token.

Request:

```json
{
  "email": "manager@civetcafe.com",
  "password": "strong-password"
}
```

### `POST /auth/refresh`

Rotates a valid refresh token and returns a new access/refresh token pair.

Request:

```json
{
  "refresh_token": "token"
}
```

### `POST /auth/logout`

Revokes the supplied refresh token.

Request:

```json
{
  "refresh_token": "token"
}
```

## RBAC

Protected routes must use `require_permission("module.action")`. Permission codes are resolved dynamically from `roles`, `permissions`, and `role_permissions` during login and refresh.

## Tables

All table routes require an API access token.

- `GET /tables` requires `tables.read`
- `GET /tables/floors` requires `tables.read`
- `POST /tables` requires `tables.manage`
- `PATCH /tables/{table_id}` requires `tables.manage`
- `DELETE /tables/{table_id}` requires `tables.manage`

## Menu

All menu routes require an API access token.

- `GET /menu/categories` requires `menu.read`
- `POST /menu/categories` requires `menu.manage`
- `PATCH /menu/categories/{category_id}` requires `menu.manage`
- `DELETE /menu/categories/{category_id}` requires `menu.manage`
- `GET /menu/items` requires `menu.read`
- `POST /menu/items` requires `menu.manage`
- `PATCH /menu/items/{item_id}` requires `menu.manage`
- `DELETE /menu/items/{item_id}` requires `menu.manage`

## Orders

All order routes require an API access token.

- `GET /orders` requires `orders.read`
- `GET /orders/{order_id}` requires `orders.read`
- `POST /orders` requires `orders.manage`
- `POST /orders/{order_id}/items` requires `orders.manage`
- `PATCH /orders/{order_id}/items/{item_id}` requires `orders.manage`
- `DELETE /orders/{order_id}/items/{item_id}` requires `orders.manage`
- `POST /orders/{order_id}/transition` requires `orders.manage`

## Billing

All billing routes require an API access token.

- `GET /billing/bills` requires `billing.read`
- `POST /billing/generate` requires `billing.manage`
- `GET /billing/bills/{bill_id}` requires `billing.read`
- `POST /billing/bills/{bill_id}/payments` requires `billing.manage`
- `GET /billing/bills/{bill_id}/receipt` requires `billing.read`
- `POST /billing/bills/{bill_id}/void` requires `billing.manage`

## Reports

All report routes require an API access token.

- `GET /reports/daily?report_date=YYYY-MM-DD` requires `reports.read`
- `GET /reports/monthly?year=YYYY&month=M` requires `reports.read`

## Users & Settings

All user and settings routes require an API access token.

- `GET /users` requires `users.read`
- `POST /users` requires `users.manage`
- `PATCH /users/{user_id}` requires `users.manage`
- `DELETE /users/{user_id}` requires `users.manage`
- `GET /roles` requires `users.read`
- `GET /permissions` requires `users.read`
- `GET /settings` requires `settings.read`
- `PUT /settings` requires `settings.manage`
- `PATCH /settings/{key}` requires `settings.manage`
