from datetime import UTC, datetime
from uuid import uuid4

from fastapi import HTTPException
from jose import jwt
from pytest import MonkeyPatch, raises

from app.api.deps import require_permission
from app.core.config import Settings, get_settings
from app.schemas.auth import CurrentUserPrincipal
from app.services.security import TokenError, TokenService


def override_settings(monkeypatch: MonkeyPatch) -> Settings:
    settings = Settings(
        database_url="postgresql+psycopg://postgres:postgres@example.com:5432/postgres",
        jwt_secret_key="test-secret",
        jwt_issuer="test-issuer",
        jwt_audience="test-audience",
    )
    get_settings.cache_clear()
    monkeypatch.setattr("app.services.security.get_settings", lambda: settings)
    return settings


def test_token_service_creates_decodable_access_token(monkeypatch: MonkeyPatch) -> None:
    override_settings(monkeypatch)
    user_id = uuid4()
    role_id = uuid4()

    token, expires_at = TokenService().create_access_token(
        user_id=user_id,
        email="manager@civetcafe.com",
        role_id=role_id,
        role_name="manager",
        permissions=["menu.read", "orders.create"],
    )

    claims = TokenService().decode_access_token(token)

    assert claims["sub"] == str(user_id)
    assert claims["role_id"] == str(role_id)
    assert claims["permissions"] == ["menu.read", "orders.create"]
    assert claims["type"] == "access"
    assert expires_at > datetime.now(UTC)


def test_token_service_rejects_non_access_token(monkeypatch: MonkeyPatch) -> None:
    settings = override_settings(monkeypatch)
    token = jwt.encode(
        {
            "sub": str(uuid4()),
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "type": "refresh",
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    with raises(TokenError):
        TokenService().decode_access_token(token)


def test_permission_dependency_allows_matching_permission() -> None:
    principal = CurrentUserPrincipal(
        user_id=uuid4(),
        email="manager@civetcafe.com",
        role_id=uuid4(),
        role_name="manager",
        permissions=frozenset({"menu.read"}),
    )

    result = require_permission("menu.read")(principal)

    assert result == principal


def test_permission_dependency_rejects_missing_permission() -> None:
    principal = CurrentUserPrincipal(
        user_id=uuid4(),
        email="cashier@civetcafe.com",
        role_id=uuid4(),
        role_name="cashier",
        permissions=frozenset({"orders.create"}),
    )

    with raises(HTTPException) as exc_info:
        require_permission("reports.read")(principal)

    assert exc_info.value.status_code == 403

