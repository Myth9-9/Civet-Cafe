from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.auth import CurrentUserPrincipal
from app.services.security import TokenError, TokenService

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUserPrincipal:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    try:
        claims = TokenService().decode_access_token(credentials.credentials)
    except TokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
        ) from exc

    return CurrentUserPrincipal(
        user_id=UUID(str(claims["sub"])),
        email=claims["email"],
        role_id=UUID(str(claims["role_id"])),
        role_name=claims["role_name"],
        permissions=frozenset(claims.get("permissions", [])),
    )


def require_permission(permission_code: str) -> Callable[[CurrentUserPrincipal], CurrentUserPrincipal]:
    def dependency(
        principal: CurrentUserPrincipal = Depends(get_current_principal),
    ) -> CurrentUserPrincipal:
        if permission_code not in principal.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied",
            )
        return principal

    return dependency

