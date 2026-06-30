from uuid import UUID

from pydantic import ValidationError
from pytest import raises

from app.api.v1.router import api_router
from app.schemas.settings import SettingUpsert
from app.schemas.users import UserCreate


def test_admin_routes_are_registered() -> None:
    paths = {route.path for route in api_router.routes}

    assert "/users" in paths
    assert "/users/{user_id}" in paths
    assert "/roles" in paths
    assert "/permissions" in paths
    assert "/settings" in paths
    assert "/settings/{key}" in paths


def test_user_create_requires_valid_email() -> None:
    with raises(ValidationError):
        UserCreate(email="bad-email", full_name="Asha Rao", role_id=UUID(int=1))


def test_setting_key_is_normalized_contract() -> None:
    payload = SettingUpsert(key="cafe.profile", value={"name": "Civet Cafe"}, is_public=True)

    assert payload.key == "cafe.profile"
