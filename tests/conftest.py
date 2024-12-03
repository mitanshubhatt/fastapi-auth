import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.server import app
from db.pg_connection import Base, get_db
from fastapi import status

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_db.sqlite"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=True)
TestSessionLocal = sessionmaker(bind=test_engine, class_=AsyncSession)

@pytest.fixture
async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

@pytest.fixture(scope="module", autouse=True)
async def setup_test_database():
    app.dependency_overrides[get_db] = override_get_db
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

@pytest_asyncio.fixture
async def setup_test_data(override_get_db):
    async with override_get_db as session:  # No parentheses here
        from auth.models import User
        from auth.utils import get_password_hash
        test_user = User(
            full_name="Test User",
            email="test@example.com",
            hashed_password=await get_password_hash("Secure@123"),
            auth_type="local"
        )
        session.add(test_user)
        await session.commit()

