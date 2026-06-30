import hashlib
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from jose import JWTError, jwt

from app.core.config import get_settings


class TokenError(ValueError):
    pass


class TokenService:
    def __init__(self) -> None:
        self._settings = get_settings()

    def create_access_token(
        self,
        *,
        user_id: uuid.UUID,
        email: str,
        role_id: uuid.UUID,
        role_name: str,
        permissions: list[str],
    ) -> tuple[str, datetime]:
        now = datetime.now(UTC)
        expires_at = now + timedelta(minutes=self._settings.access_token_expire_minutes)
        claims: dict[str, Any] = {
            "iss": self._settings.jwt_issuer,
            "aud": self._settings.jwt_audience,
            "sub": str(user_id),
            "email": email,
            "role_id": str(role_id),
            "role_name": role_name,
            "permissions": permissions,
            "iat": int(now.timestamp()),
            "exp": expires_at,
            "type": "access",
            "jti": str(uuid.uuid4()),
        }
        token = jwt.encode(claims, self._settings.jwt_secret_key, algorithm=self._settings.jwt_algorithm)
        return token, expires_at

    def decode_access_token(self, token: str) -> dict[str, Any]:
        try:
            claims = jwt.decode(
                token,
                self._settings.jwt_secret_key,
                algorithms=[self._settings.jwt_algorithm],
                audience=self._settings.jwt_audience,
                issuer=self._settings.jwt_issuer,
            )
        except JWTError as exc:
            raise TokenError("Invalid access token") from exc

        if claims.get("type") != "access":
            raise TokenError("Invalid token type")
        return claims

    def create_refresh_token(self) -> tuple[str, str, datetime]:
        raw_token = secrets.token_urlsafe(64)
        token_hash = self.hash_refresh_token(raw_token)
        expires_at = datetime.now(UTC) + timedelta(days=self._settings.refresh_token_expire_days)
        return raw_token, token_hash, expires_at

    def hash_refresh_token(self, raw_token: str) -> str:
        keyed_value = f"{raw_token}.{self._settings.jwt_secret_key}".encode("utf-8")
        return hashlib.sha256(keyed_value).hexdigest()

