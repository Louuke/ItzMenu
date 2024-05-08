import asyncio

import httpx
import pytest
import pytest_asyncio

from itzmenu_service import app
from itzmenu_service.manager.users import get_user_manager
from itzmenu_service.persistence.database import get_user_db


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


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(app=app.app, base_url="http://127.0.0.1:8000")


@pytest_asyncio.fixture
async def user_db():
    return await get_user_db().__anext__()


@pytest_asyncio.fixture
async def user_manager(user_db):
    return await get_user_manager(user_db).__anext__()
