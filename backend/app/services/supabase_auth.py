import uuid
from dataclasses import dataclass

from supabase import Client, create_client

from app.core.config import get_settings


@dataclass(frozen=True)
class SupabaseIdentity:
    user_id: uuid.UUID
    email: str


class SupabaseAuthError(ValueError):
    pass


class SupabaseAuthGateway:
    def __init__(self, client: Client | None = None) -> None:
        settings = get_settings()
        if client is not None:
            self._client = client
            return
        if not settings.supabase_url or not settings.supabase_anon_key:
            raise RuntimeError("Supabase URL and anon key must be configured")
        self._client = create_client(settings.supabase_url, settings.supabase_anon_key)

    def sign_in_with_password(self, email: str, password: str) -> SupabaseIdentity:
        try:
            response = self._client.auth.sign_in_with_password(
                {"email": email.lower(), "password": password}
            )
        except Exception as exc:  # Supabase client raises provider-specific exceptions.
            raise SupabaseAuthError("Invalid email or password") from exc

        user = getattr(response, "user", None)
        user_id = getattr(user, "id", None)
        user_email = getattr(user, "email", None)
        if not user_id or not user_email:
            raise SupabaseAuthError("Invalid email or password")

        return SupabaseIdentity(user_id=uuid.UUID(str(user_id)), email=str(user_email).lower())

