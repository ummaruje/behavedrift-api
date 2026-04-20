import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import AsyncGenerator

from app.main import app
from app.database import Base, get_db
from app.models.tenant import Tenant
from app.auth.jwt import create_access_token

# Use an in-memory SQLite database for integration testing.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestingSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_setup():
    """Create and drop all tables before and after each test."""
    # SQLite requires special foreign key handling, but for simple tests
    # creating tables is enough.
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a DB session specifically for test setup."""
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Yield an HTTPX test client."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://testserver"
    ) as ac:
        yield ac


@pytest_asyncio.fixture(scope="function")
async def active_tenant(db_session: AsyncSession) -> Tenant:
    """Create and return an active tenant."""
    tenant = Tenant(
        organisation_name="Test Automation Corp",
        contact_email="test@automation.corp",
        plan="self_hosted",
        client_id="test_client_id_123",
        client_secret_hash="fake_hash",
        is_active=True
    )
    db_session.add(tenant)
    await db_session.commit()
    await db_session.refresh(tenant)
    return tenant


@pytest.fixture(scope="function")
def active_tenant_token(active_tenant: Tenant) -> str:
    """Generate a valid mock JWT token for the active test tenant."""
    return create_access_token(
        subject=active_tenant.client_id,
        tenant_id=active_tenant.id,
        scopes=["read:alerts", "write:alerts", "read:observations"],
    )
