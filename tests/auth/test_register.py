# test_register.py

import pytest
from httpx import AsyncClient
from app.server import app
from auth.models import User
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, db_session: AsyncSession):
    response = await client.post("/auth/register", json={
        "full_name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert "id" in data

    # Check if user is in the database
    user = await db_session.get(User, data["id"])
    assert user is not None
    assert user.email == "test@example.com"

@pytest.mark.asyncio
async def test_create_existing_user(client: AsyncClient, db_session: AsyncSession):
    # First, create a user
    await client.post("/auth/register", json={
        "full_name": "Existing User",
        "email": "existing@example.com",
        "password": "existingpassword123"
    })

    # Try to create the same user again
    response = await client.post("/auth/register", json={
        "full_name": "Existing User",
        "email": "existing@example.com",
        "password": "existingpassword123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "User already registered."
