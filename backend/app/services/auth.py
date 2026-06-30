from sqlalchemy.orm import Session

from app.models.auth import RefreshToken
from app.models.user import User
from app.repositories.rbac import RolePermissionRepository
from app.repositories.refresh_tokens import RefreshTokenRepository
from app.repositories.users import UserRepository
from app.schemas.auth import AuthUserResponse, TokenPairResponse
from app.services.security import TokenService
from app.services.supabase_auth import SupabaseAuthGateway


class AuthenticationError(ValueError):
    pass


class AuthorizationStateError(ValueError):
    pass


class AuthService:
    def __init__(
        self,
        db: Session,
        supabase_auth: SupabaseAuthGateway | None = None,
        token_service: TokenService | None = None,
    ) -> None:
        self._db = db
        self._users = UserRepository(db)
        self._permissions = RolePermissionRepository(db)
        self._refresh_tokens = RefreshTokenRepository(db)
        self._supabase_auth = supabase_auth or SupabaseAuthGateway()
        self._token_service = token_service or TokenService()

    def login(
        self,
        *,
        email: str,
        password: str,
        user_agent: str | None,
        ip_address: str | None,
    ) -> TokenPairResponse:
        identity = self._supabase_auth.sign_in_with_password(email, password)
        user = self._users.get_active_by_supabase_user_id(identity.user_id)
        if user is None:
            user = self._users.get_active_by_email(identity.email)

        if user is None:
            raise AuthorizationStateError("Authenticated Supabase user is not provisioned in POS")

        return self._issue_token_pair(user=user, user_agent=user_agent, ip_address=ip_address)

    def refresh(
        self,
        *,
        raw_refresh_token: str,
        user_agent: str | None,
        ip_address: str | None,
    ) -> TokenPairResponse:
        token_hash = self._token_service.hash_refresh_token(raw_refresh_token)
        existing = self._refresh_tokens.get_active_by_hash(token_hash)
        if existing is None:
            raise AuthenticationError("Invalid refresh token")

        user = self._users.get_active_by_id(existing.user_id)
        if user is None:
            raise AuthenticationError("Refresh token user is no longer active")

        response = self._issue_token_pair(
            user=user,
            user_agent=user_agent,
            ip_address=ip_address,
            commit=False,
        )
        new_token_hash = self._token_service.hash_refresh_token(response.refresh_token)
        replacement = self._refresh_tokens.get_active_by_hash(new_token_hash)
        self._refresh_tokens.revoke(existing, replacement.id if replacement else None)
        self._db.commit()
        return response

    def logout(self, *, raw_refresh_token: str) -> None:
        token_hash = self._token_service.hash_refresh_token(raw_refresh_token)
        existing = self._refresh_tokens.get_active_by_hash(token_hash)
        if existing is not None:
            self._refresh_tokens.revoke(existing)
            self._db.commit()

    def _issue_token_pair(
        self,
        *,
        user: User,
        user_agent: str | None,
        ip_address: str | None,
        commit: bool = True,
    ) -> TokenPairResponse:
        role_name = self._users.get_role_name(user.role_id)
        permissions = self._permissions.list_permission_codes_for_role(user.role_id)
        access_token, access_expires_at = self._token_service.create_access_token(
            user_id=user.id,
            email=user.email,
            role_id=user.role_id,
            role_name=role_name,
            permissions=permissions,
        )
        refresh_token, refresh_token_hash, refresh_expires_at = self._token_service.create_refresh_token()
        self._refresh_tokens.add(
            RefreshToken(
                user_id=user.id,
                token_hash=refresh_token_hash,
                expires_at=refresh_expires_at,
                user_agent=user_agent,
                ip_address=ip_address,
            )
        )
        if commit:
            self._db.commit()

        return TokenPairResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=access_expires_at,
            user=AuthUserResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                role_id=user.role_id,
                role_name=role_name,
                permissions=permissions,
            ),
        )
