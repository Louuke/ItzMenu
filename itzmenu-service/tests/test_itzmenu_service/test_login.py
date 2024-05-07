import asyncio
import typing as tp

from itzmenu_service import app
import httpx
import pytest
from beanie import init_beanie

from itzmenu_service.manager.users import get_user_manager
from itzmenu_service.persistence.database import db, get_user_db
from itzmenu_service.persistence.models import User


@pytest.fixture(scope='session')
def event_loop(request):
    """ Create an instance of the default event loop for each test case. """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session', autouse=True)
def prepare_database(event_loop):
    async def init():
        async with app.lifespan():
            pass
    event_loop.run_until_complete(init())


@pytest.mark.asyncio
async def test_register(prepare_database):
    # response = await jwt_authorized_async_client.get('/users/me')
    # assert response.status_code == 200
    #
    # data = response.json()
    # print(data)
    user_db = await get_user_db().__anext__()
    manager = await get_user_manager(user_db=user_db).__anext__()
    from fastapi_users.schemas import BaseUserCreate, EmailStr
    user = await manager.get_by_email('fastapi@jannsen.org')
    print(user)


@pytest.mark.asyncio
async def test_register2(prepare_database):
    # response = await jwt_authorized_async_client.get('/users/me')
    # assert response.status_code == 200
    #
    # data = response.json()
    # print(data)
    user_db = await get_user_db().__anext__()
    manager = await get_user_manager(user_db=user_db).__anext__()
    from fastapi_users.schemas import BaseUserCreate, EmailStr
    user = await manager.get_by_email('fastapi@jannsen.org')
    print(user)
