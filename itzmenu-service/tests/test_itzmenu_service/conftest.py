import asyncio
import os

import httpx
import pytest
import pytest_asyncio

from itzmenu_service import app
from itzmenu_service.manager.users import get_user_manager
from itzmenu_service.persistence.database import get_user_db
from itzmenu_service.persistence.models import User


@pytest.fixture(scope='session', autouse=True)
def override_settings():
    os.environ['mongo_db_name'] = 'test'
    os.environ['mail_smtp_host'] = '127.0.0.1'
    os.environ['mail_smtp_port'] = '42000'
    os.environ['mail_smtp_tls'] = 'false'
    os.environ['mail_smtp_skip_login'] = 'true'


@pytest.fixture(scope='session', autouse=True)
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def prepare_database():
    async with app.lifespan():
        await User.find().delete()


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(app=app.app, base_url="http://127.0.0.1:8000")


@pytest_asyncio.fixture
async def user_db():
    return await get_user_db().__anext__()


@pytest_asyncio.fixture
async def user_manager(user_db):
    return await get_user_manager(user_db).__anext__()
