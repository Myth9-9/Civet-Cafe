from __future__ import annotations

import uuid
from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import Session, sessionmaker

# 1. Register SQLite compiler rule for JSONB
@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

from app.db.base import Base
from app.db.session import get_db_session
from app.main import app
from app.models.rbac import Permission, Role, RolePermission
from app.models.user import User
from app.services.security import TokenService
from app.services.supabase_auth import SupabaseAuthGateway, SupabaseIdentity


from sqlalchemy import event

@pytest.fixture(scope="session")
def engine():
    # Create SQLite in-memory engine
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        future=True,
    )
    
    @event.listens_for(test_engine, "connect")
    def register_sqlite_functions(dbapi_connection, connection_record):
        dbapi_connection.create_function("gen_random_uuid", 0, lambda: uuid.uuid4().hex)

    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    return test_engine


@pytest.fixture(scope="session")
def TestingSessionLocal(engine) -> sessionmaker[Session]:
    return sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)


@pytest.fixture
def db(TestingSessionLocal) -> Generator[Session, None, None]:
    # Yield a transactional session
    connection = TestingSessionLocal.kw["bind"].connect()
    transaction = connection.begin()
    session = Session(bind=connection, expire_on_commit=False)

    yield session

    session.close()
    if transaction.is_active:
        transaction.rollback()
    connection.close()


@pytest.fixture
def mock_supabase_auth(monkeypatch) -> MagicMock:
    # Mock SupabaseAuthGateway to prevent actual API calls
    mock_gateway = MagicMock(spec=SupabaseAuthGateway)
    monkeypatch.setattr("app.services.auth.SupabaseAuthGateway", lambda: mock_gateway)
    return mock_gateway


@pytest.fixture
def client(db) -> Generator[TestClient, None, None]:
    # Override get_db_session dependency to use the transactional test db session
    def override_get_db() -> Generator[Session, None, None]:
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db_session] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def seed_rbac(db) -> dict[str, MagicMock | uuid.UUID | Role | Permission]:
    # Helper to seed default roles and permissions
    admin_role = Role(
        id=uuid.uuid4(),
        name="admin",
        description="System Administrator",
        is_system=True,
    )
    cashier_role = Role(
        id=uuid.uuid4(),
        name="cashier",
        description="Cashier Staff",
        is_system=False,
    )
    
    db.add(admin_role)
    db.add(cashier_role)
    
    # Add permissions
    permissions = [
        Permission(id=uuid.uuid4(), code="menu.read", module="menu", action="read"),
        Permission(id=uuid.uuid4(), code="menu.write", module="menu", action="write"),
        Permission(id=uuid.uuid4(), code="orders.read", module="orders", action="read"),
        Permission(id=uuid.uuid4(), code="orders.write", module="orders", action="write"),
        Permission(id=uuid.uuid4(), code="billing.read", module="billing", action="read"),
        Permission(id=uuid.uuid4(), code="billing.write", module="billing", action="write"),
        Permission(id=uuid.uuid4(), code="reports.read", module="reports", action="read"),
        Permission(id=uuid.uuid4(), code="admin.read", module="admin", action="read"),
        Permission(id=uuid.uuid4(), code="admin.write", module="admin", action="write"),
    ]
    
    for perm in permissions:
        db.add(perm)
        
    db.flush()
    
    # Associate permissions with roles
    # Admin gets all
    for perm in permissions:
        db.add(RolePermission(id=uuid.uuid4(), role_id=admin_role.id, permission_id=perm.id))
        
    # Cashier gets menu.read, orders.write, orders.read, billing.write, billing.read
    cashier_perms = {"menu.read", "orders.write", "orders.read", "billing.write", "billing.read"}
    for perm in permissions:
        if perm.code in cashier_perms:
            db.add(RolePermission(id=uuid.uuid4(), role_id=cashier_role.id, permission_id=perm.id))
            
    db.commit()
    
    return {
        "admin_role": admin_role,
        "cashier_role": cashier_role,
        "permissions": {p.code: p for p in permissions},
    }


@pytest.fixture
def auth_headers(seed_rbac):
    # Generates standard auth headers for request testing
    def _headers(role_name: str, permissions: list[str]) -> dict[str, str]:
        role = seed_rbac["admin_role"] if role_name == "admin" else seed_rbac["cashier_role"]
        token, _ = TokenService().create_access_token(
            user_id=uuid.uuid4(),
            email=f"{role_name}@civetcafe.com",
            role_id=role.id,
            role_name=role.name,
            permissions=permissions,
        )
        return {"Authorization": f"Bearer {token}"}
    return _headers
