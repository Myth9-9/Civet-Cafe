from __future__ import annotations

import uuid

import pytest

from app.models.user import User
from app.schemas.settings import SettingUpsert, SettingUpdate
from app.schemas.users import UserCreate, UserUpdate
from app.services.admin import AdminNotFoundError, AdminValidationError, SettingsService, UserAdminService


class TestUserAdminService:
    def test_list_users_returns_only_active(self, db, seed_rbac):
        role = seed_rbac["admin_role"]

        user1 = User(id=uuid.uuid4(), role_id=role.id, email="active@civetcafe.com", full_name="Active User", is_active=True)
        user2 = User(id=uuid.uuid4(), role_id=role.id, email="inactive@civetcafe.com", full_name="Inactive User", is_active=False)
        db.add_all([user1, user2])
        db.commit()

        svc = UserAdminService(db)
        result = svc.list_users(include_inactive=False, limit=20, offset=0)
        emails = {u.email for u in result}
        assert "active@civetcafe.com" in emails
        assert "inactive@civetcafe.com" not in emails

    def test_list_users_include_inactive(self, db, seed_rbac):
        role = seed_rbac["admin_role"]
        user1 = User(id=uuid.uuid4(), role_id=role.id, email="active@civetcafe.com", full_name="Active User", is_active=True)
        user2 = User(id=uuid.uuid4(), role_id=role.id, email="inactive@civetcafe.com", full_name="Inactive User", is_active=False)
        db.add_all([user1, user2])
        db.commit()

        svc = UserAdminService(db)
        result = svc.list_users(include_inactive=True, limit=20, offset=0)
        assert len(result) >= 2

    def test_create_user_succeeds(self, db, seed_rbac):
        role = seed_rbac["cashier_role"]
        svc = UserAdminService(db)
        payload = UserCreate(
            email="newuser@civetcafe.com",
            full_name="New User",
            role_id=role.id,
            employee_code="EMP-NEW",
        )
        user = svc.create_user(payload)
        assert user.email == "newuser@civetcafe.com"
        assert user.full_name == "New User"
        assert user.role_id == role.id
        assert user.is_active is True

    def test_create_user_duplicate_email_raises_error(self, db, seed_rbac):
        role = seed_rbac["cashier_role"]
        existing = User(id=uuid.uuid4(), role_id=role.id, email="dup@civetcafe.com", full_name="Dup User", is_active=True)
        db.add(existing)
        db.commit()

        svc = UserAdminService(db)
        payload = UserCreate(email="dup@civetcafe.com", full_name="Another Dup", role_id=role.id)
        with pytest.raises(AdminValidationError, match="email already exists"):
            svc.create_user(payload)

    def test_create_user_duplicate_employee_code_raises_error(self, db, seed_rbac):
        role = seed_rbac["cashier_role"]
        existing = User(id=uuid.uuid4(), role_id=role.id, email="existing@civetcafe.com", full_name="Existing", employee_code="EMP-01", is_active=True)
        db.add(existing)
        db.commit()

        svc = UserAdminService(db)
        payload = UserCreate(email="new@civetcafe.com", full_name="New", role_id=role.id, employee_code="EMP-01")
        with pytest.raises(AdminValidationError, match="Employee code already exists"):
            svc.create_user(payload)

    def test_create_user_invalid_role_raises_error(self, db):
        svc = UserAdminService(db)
        payload = UserCreate(email="badrole@civetcafe.com", full_name="Bad Role", role_id=uuid.uuid4())
        with pytest.raises(AdminValidationError, match="Role does not exist"):
            svc.create_user(payload)

    def test_update_user_succeeds(self, db, seed_rbac):
        role = seed_rbac["cashier_role"]
        user = User(id=uuid.uuid4(), role_id=role.id, email="update@civetcafe.com", full_name="Original Name", is_active=True)
        db.add(user)
        db.commit()

        svc = UserAdminService(db)
        payload = UserUpdate(full_name="Updated Name", phone="+919999999999")
        updated = svc.update_user(user.id, payload)
        assert updated.full_name == "Updated Name"
        assert updated.phone == "+919999999999"

    def test_update_user_not_found_raises_error(self, db):
        svc = UserAdminService(db)
        payload = UserUpdate(full_name="Ghost")
        with pytest.raises(AdminNotFoundError, match="User not found"):
            svc.update_user(uuid.uuid4(), payload)

    def test_update_user_duplicate_employee_code_raises_error(self, db, seed_rbac):
        role = seed_rbac["cashier_role"]
        user1 = User(id=uuid.uuid4(), role_id=role.id, email="user1@civetcafe.com", full_name="User One", employee_code="EMP-01", is_active=True)
        user2 = User(id=uuid.uuid4(), role_id=role.id, email="user2@civetcafe.com", full_name="User Two", employee_code="EMP-02", is_active=True)
        db.add_all([user1, user2])
        db.commit()

        svc = UserAdminService(db)
        payload = UserUpdate(employee_code="EMP-02")
        with pytest.raises(AdminValidationError, match="Employee code already exists"):
            svc.update_user(user1.id, payload)

    def test_delete_user_soft_deletes(self, db, seed_rbac):
        role = seed_rbac["cashier_role"]
        user = User(id=uuid.uuid4(), role_id=role.id, email="todelete@civetcafe.com", full_name="Delete Me", is_active=True)
        db.add(user)
        db.commit()

        svc = UserAdminService(db)
        svc.delete_user(user.id)
        db.refresh(user)
        assert user.deleted_at is not None
        assert user.is_active is False

    def test_delete_user_not_found_raises_error(self, db):
        svc = UserAdminService(db)
        with pytest.raises(AdminNotFoundError, match="User not found"):
            svc.delete_user(uuid.uuid4())

    def test_list_roles(self, db, seed_rbac):
        svc = UserAdminService(db)
        roles = svc.list_roles()
        names = {r.name for r in roles}
        assert "admin" in names
        assert "cashier" in names

    def test_list_permissions(self, db, seed_rbac):
        svc = UserAdminService(db)
        perms = svc.list_permissions()
        codes = {p.code for p in perms}
        assert "menu.read" in codes
        assert "menu.write" in codes


class TestSettingsService:
    def test_upsert_creates_new_setting(self, db):
        svc = SettingsService(db)
        payload = SettingUpsert(key="cafe.profile", value={"name": "Civet Cafe"}, is_public=True)
        setting = svc.upsert(payload)
        assert setting.key == "cafe.profile"
        assert setting.value == {"name": "Civet Cafe"}
        assert setting.is_public is True

    def test_upsert_updates_existing_setting(self, db):
        svc = SettingsService(db)
        payload = SettingUpsert(key="cafe.profile", value={"name": "Civet Cafe"}, is_public=True)
        svc.upsert(payload)

        payload2 = SettingUpsert(key="cafe.profile", value={"name": "Civet Cafe Updated"}, is_public=False)
        updated = svc.upsert(payload2)
        assert updated.value == {"name": "Civet Cafe Updated"}
        assert updated.is_public is False

    def test_list_settings(self, db):
        svc = SettingsService(db)
        svc.upsert(SettingUpsert(key="cafe.name", value={"name": "Test Cafe"}, is_public=True))
        svc.upsert(SettingUpsert(key="internal.key", value={"secret": "true"}, is_public=False))

        all_settings = svc.list(public_only=False)
        assert len(all_settings) == 2

        public_only = svc.list(public_only=True)
        assert len(public_only) == 1
        assert public_only[0].key == "cafe.name"

    def test_update_existing_setting(self, db):
        svc = SettingsService(db)
        svc.upsert(SettingUpsert(key="cafe.name", value={"name": "Original"}, is_public=True))

        updated = svc.update("cafe.name", SettingUpdate(value={"name": "Updated"}, is_public=False))
        assert updated.value == {"name": "Updated"}
        assert updated.is_public is False

    def test_update_nonexistent_setting_raises_error(self, db):
        svc = SettingsService(db)
        with pytest.raises(AdminNotFoundError, match="Setting not found"):
            svc.update("nonexistent.key", SettingUpdate(value={"x": "y"}))
