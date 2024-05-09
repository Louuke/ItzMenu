import os

import httpx
import pytest
import pytest_asyncio
from httpx import ASGITransport

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


@pytest_asyncio.fixture(scope='session', autouse=True)
async def prepare_database():
    async with app.lifespan():
        await User.find().delete()


@pytest.fixture
def http_client() -> httpx.AsyncClient:
    return httpx.AsyncClient(transport=ASGITransport(app=app.app), base_url="http://127.0.0.1:8000")


@pytest_asyncio.fixture
async def user_db():
    return await get_user_db().__anext__()


@pytest_asyncio.fixture
async def user_manager(user_db):
    return await get_user_manager(user_db).__anext__()
