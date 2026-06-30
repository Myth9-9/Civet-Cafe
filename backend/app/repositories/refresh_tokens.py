import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.auth import RefreshToken


class RefreshTokenRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, refresh_token: RefreshToken) -> RefreshToken:
        self._db.add(refresh_token)
        self._db.flush()
        return refresh_token

    def get_active_by_hash(self, token_hash: str) -> RefreshToken | None:
        statement = (
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .where(RefreshToken.revoked_at.is_(None))
            .where(RefreshToken.expires_at > datetime.now(UTC))
        )
        return self._db.execute(statement).scalar_one_or_none()

    def revoke(
        self,
        refresh_token: RefreshToken,
        replaced_by_token_id: uuid.UUID | None = None,
    ) -> None:
        refresh_token.revoked_at = datetime.now(UTC)
        refresh_token.replaced_by_token_id = replaced_by_token_id  # type: ignore[assignment]
        self._db.flush()
