import pytest
from httpx import AsyncClient, ASGITransport

from src.main import app
from src.database import PrivateUser


@pytest.mark.asyncio
async def test_list_users():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        response = await c.get("/users")
        assert response.status_code == 200

        data = response.json()
        assert len(data) == 4


@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        user = PrivateUser(email="user@example.ru", password="1234")
        response = await c.post("/users", json=user.model_dump())
        assert response.status_code == 400

        data = response.json()
        assert data.get("detail") == f"User with this email {user.email} already exists"
