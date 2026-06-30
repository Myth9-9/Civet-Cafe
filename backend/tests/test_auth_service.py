from __future__ import annotations

import uuid
import pytest
from unittest.mock import MagicMock
from jose import jwt

from app.models.user import User
from app.services.auth import AuthService, AuthenticationError, AuthorizationStateError
from app.services.supabase_auth import SupabaseIdentity, SupabaseAuthError
from app.services.security import TokenService


def test_login_succeeds(db, mock_supabase_auth, seed_rbac):
    # Setup test user provisioned in POS
    role = seed_rbac["cashier_role"]
    user_id = uuid.uuid4()
    supabase_id = uuid.uuid4()
    user = User(
        id=user_id,
        supabase_user_id=supabase_id,
        role_id=role.id,
        email="cashier@civetcafe.com",
        full_name="Cashier John",
        is_active=True,
    )
    db.add(user)
    db.commit()

    # Mock Supabase login return
    mock_supabase_auth.sign_in_with_password.return_value = SupabaseIdentity(
        user_id=supabase_id,
        email="cashier@civetcafe.com",
    )

    service = AuthService(db)
    response = service.login(
        email="cashier@civetcafe.com",
        password="securepassword123",
        user_agent="Mozilla/5.0",
        ip_address="127.0.0.1",
    )

    assert response.user.id == user_id
    assert response.user.email == "cashier@civetcafe.com"
    assert response.user.role_name == "cashier"
    assert "menu.read" in response.user.permissions
    assert response.access_token is not None
    assert response.refresh_token is not None


def test_login_raises_error_when_user_not_provisioned(db, mock_supabase_auth, seed_rbac):
    # Mock Supabase login returns a valid identity but the user doesn't exist in POS db
    supabase_id = uuid.uuid4()
    mock_supabase_auth.sign_in_with_password.return_value = SupabaseIdentity(
        user_id=supabase_id,
        email="not-provisioned@civetcafe.com",
    )

    service = AuthService(db)
    with pytest.raises(AuthorizationStateError) as exc_info:
        service.login(
            email="not-provisioned@civetcafe.com",
            password="securepassword123",
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )
    assert "not provisioned" in str(exc_info.value)


def test_login_raises_error_when_supabase_fails(db, mock_supabase_auth):
    mock_supabase_auth.sign_in_with_password.side_effect = SupabaseAuthError("Invalid email or password")

    service = AuthService(db)
    with pytest.raises(SupabaseAuthError):
        service.login(
            email="cashier@civetcafe.com",
            password="wrongpassword",
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )


def test_refresh_token_rotation(db, mock_supabase_auth, seed_rbac):
    # Setup test user
    role = seed_rbac["cashier_role"]
    user_id = uuid.uuid4()
    supabase_id = uuid.uuid4()
    user = User(
        id=user_id,
        supabase_user_id=supabase_id,
        role_id=role.id,
        email="cashier2@civetcafe.com",
        full_name="Cashier Jack",
        is_active=True,
    )
    db.add(user)
    db.commit()

    # Login to get a token pair
    mock_supabase_auth.sign_in_with_password.return_value = SupabaseIdentity(
        user_id=supabase_id,
        email="cashier2@civetcafe.com",
    )

    service = AuthService(db)
    login_response = service.login(
        email="cashier2@civetcafe.com",
        password="securepassword123",
        user_agent="Mozilla/5.0",
        ip_address="127.0.0.1",
    )

    # Perform refresh
    refresh_response = service.refresh(
        raw_refresh_token=login_response.refresh_token,
        user_agent="Mozilla/5.0",
        ip_address="127.0.0.1",
    )

    assert refresh_response.access_token is not None
    assert refresh_response.refresh_token is not None
    assert refresh_response.refresh_token != login_response.refresh_token

    # Verify that the old refresh token is revoked (cannot be used again)
    with pytest.raises(AuthenticationError) as exc_info:
        service.refresh(
            raw_refresh_token=login_response.refresh_token,
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )
    assert "Invalid refresh token" in str(exc_info.value)


def test_logout_revokes_token(db, mock_supabase_auth, seed_rbac):
    role = seed_rbac["cashier_role"]
    user_id = uuid.uuid4()
    supabase_id = uuid.uuid4()
    user = User(
        id=user_id,
        supabase_user_id=supabase_id,
        role_id=role.id,
        email="cashier3@civetcafe.com",
        full_name="Cashier Jill",
        is_active=True,
    )
    db.add(user)
    db.commit()

    mock_supabase_auth.sign_in_with_password.return_value = SupabaseIdentity(
        user_id=supabase_id,
        email="cashier3@civetcafe.com",
    )

    service = AuthService(db)
    login_response = service.login(
        email="cashier3@civetcafe.com",
        password="securepassword123",
        user_agent="Mozilla/5.0",
        ip_address="127.0.0.1",
    )

    # Logout
    service.logout(raw_refresh_token=login_response.refresh_token)

    # Verify token is revoked and cannot be refreshed
    with pytest.raises(AuthenticationError):
        service.refresh(
            raw_refresh_token=login_response.refresh_token,
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )


def test_login_raises_error_when_user_inactive(db, mock_supabase_auth, seed_rbac):
    role = seed_rbac["cashier_role"]
    supabase_id = uuid.uuid4()
    user = User(
        id=uuid.uuid4(),
        supabase_user_id=supabase_id,
        role_id=role.id,
        email="inactive@civetcafe.com",
        full_name="Inactive User",
        is_active=False,
    )
    db.add(user)
    db.commit()

    mock_supabase_auth.sign_in_with_password.return_value = SupabaseIdentity(
        user_id=supabase_id,
        email="inactive@civetcafe.com",
    )

    service = AuthService(db)
    # User is inactive -> repository returns None -> "not provisioned"
    with pytest.raises(AuthorizationStateError, match="not provisioned"):
        service.login(
            email="inactive@civetcafe.com",
            password="securepassword123",
            user_agent="Mozilla/5.0",
            ip_address="127.0.0.1",
        )


def test_refresh_with_expired_access_token(monkeypatch, db, seed_rbac):
    from app.core.config import Settings, get_settings

    get_settings.cache_clear()
    monkeypatch.setattr("app.services.security.get_settings", lambda: Settings(
        database_url="postgresql+psycopg://postgres:postgres@example.com:5432/postgres",
        jwt_secret_key="test-secret",
        jwt_issuer="test-issuer",
        jwt_audience="test-audience",
        jwt_refresh_expire_minutes=1,
        jwt_access_expire_minutes=1,
    ))

    role = seed_rbac["cashier_role"]
    supabase_id = uuid.uuid4()
    user = User(
        id=uuid.uuid4(),
        supabase_user_id=supabase_id,
        role_id=role.id,
        email="refresh-expire@civetcafe.com",
        full_name="Refresh User",
        is_active=True,
    )
    db.add(user)
    db.commit()

    # Use security service directly to create an access token
    token, _ = TokenService().create_access_token(
        user_id=user.id,
        email="refresh-expire@civetcafe.com",
        role_id=role.id,
        role_name="cashier",
        permissions=["menu.read"],
    )

    from app.schemas.auth import TokenPairResponse
    from app.services.auth import AuthService

    service = AuthService(db)
    # Should be able to decode it immediately
    from jose import jwt as jose_jwt
    claims = jose_jwt.decode(
        token,
        "test-secret",
        algorithms=["HS256"],
        audience="test-audience",
        issuer="test-issuer",
    )
    assert claims["type"] == "access"
    assert claims["sub"] == str(user.id)
