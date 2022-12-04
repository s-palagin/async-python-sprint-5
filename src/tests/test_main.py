from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from .mocks import CustomTestUser
from core.config import BASE_DIR


test_user = CustomTestUser()


async def test_register_user(
    client: AsyncClient, async_session: AsyncSession
) -> None:
    response = await client.post(
        '/register',
        json={
            'name': test_user.name,
            'password': test_user.password
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert 'name' in response.json()
    assert response.json().get('name') == test_user.name
    assert 'id' in response.json()


async def test_get_token(
    client: AsyncClient, async_session: AsyncSession
) -> None:
    response = await client.post(
        '/auth', data={
            'username': test_user.name,
            'password': test_user.password
        }
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert 'access_token' in response.json()
    assert 'expires' in response.json()
    assert 'token_type' in response.json()
    assert response.json().get('token_type') == 'bearer'
    test_user.set_token(response.json().get('access_token'))


async def test_get_user_info(
    client: AsyncClient, async_session: AsyncSession
) -> None:
    response = await client.get(
        '/me',
        headers={'Authorization': f'Bearer {test_user.token}'}
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'name' in response.json()
    assert response.json().get('name') == test_user.name
    assert 'id' in response.json()
    assert response.json().get('id') == 1


async def test_get_availability_services(
    client: AsyncClient, async_session: AsyncSession
) -> None:
    response = await client.get(
        '/ping',
        headers={'Authorization': f'Bearer {test_user.token}'}
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'datebase' in response.json()
    assert 'redis' in response.json()
    assert 'user' in response.json()


async def test_upload_file(
    client: AsyncClient, async_session: AsyncSession
) -> None:
    response = await client.post(
        '/upload', params={'path': 'test_dir'}, files={
            'file': (
                'test_file.txt',
                open(BASE_DIR + '/tests/test_file.txt', 'rb')
            )
        },
        headers={'Authorization': f'Bearer {test_user.token}'}
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert 'Ready' in response.json()
    assert response.json().get('Ready') == (
        'Successfully uploaded test_file.txt')
    assert 'Size' in response.json()


async def test_get_file_list(
    client: AsyncClient, async_session: AsyncSession
) -> None:
    response = await client.get(
        '/list',
        headers={'Authorization': f'Bearer {test_user.token}'}
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'items' in response.json()
    assert isinstance(response.json().get('items'), list)
    assert len(response.json().get('items')) == 1
    assert 'total' in response.json()
    assert response.json().get('total') == 1
