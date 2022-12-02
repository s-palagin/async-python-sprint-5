import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
# from .mocks import TEST_LINKS, TEST_LINKS_ID, TESTS_COUNT


async def test_create_item(
    client: AsyncClient, async_session: AsyncSession
) -> None:
    response = await client.post(
        app.url_path_for('ping'), {'name': 'Test User', 'password': 'test_password'})

    assert response.status_code == status.HTTP_201_CREATED
