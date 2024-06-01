import os
from uuid import UUID

import pytest
import pytest_asyncio
from fastapi_users import BaseUserManager
from fastapi_users.jwt import generate_jwt
from fastapi_users.password import PasswordHelper
from fastapi_users_db_beanie import BeanieUserDatabase
from httpx import AsyncClient, ASGITransport

from itzmenu_service import app
from itzmenu_service.config.settings import Settings
from itzmenu_service.manager.users import get_user_manager
from itzmenu_service.manager.menus import get_week_menu_manager
from itzmenu_service.persistence.adapter.adapter import BeanieWeekMenuDatabase
from itzmenu_service.persistence.database import get_user_db, get_menu_db
from itzmenu_service.persistence.models import User, WeekMenu


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
        await WeekMenu.find().delete()


@pytest.fixture(scope='session')
def user_pwd() -> str:
    return 'paSSw0rd'


@pytest.fixture(scope='session')
def user_hashed_pwd(user_pwd: str) -> str:
    return PasswordHelper().hash(user_pwd)


@pytest_asyncio.fixture(scope='session')
async def user_w_permissions(user_hashed_pwd: str) -> User:
    email = 'user_w_permissions@example.org'
    permissions = ['menus:create_menu', 'menus:update_menu', 'menus:delete_menu']
    return await User(email=email, hashed_password=user_hashed_pwd, permissions=permissions).create()


@pytest_asyncio.fixture(scope='session')
async def user_wo_permissions(user_hashed_pwd: str) -> User:
    email = 'user_wo_permissions@example.org'
    return await User(email=email, hashed_password=user_hashed_pwd).create()


@pytest_asyncio.fixture(scope='session')
async def user_superuser(user_hashed_pwd: str) -> User:
    email = 'superuser@example.org'
    return await User(email=email, hashed_password=user_hashed_pwd, is_superuser=True).create()


@pytest_asyncio.fixture(scope='session')
async def user_inactive(user_hashed_pwd: str) -> User:
    email = 'user_inactive@example.org'
    user = await User(email=email, hashed_password=user_hashed_pwd).create()
    user.is_active = False
    await user.save()
    return await User.find_one(User.id == user.id)


@pytest_asyncio.fixture(scope='session')
async def user_w_permissions_headers(user_w_permissions: User) -> dict[str, str]:
    return __create_headers(user_w_permissions)


@pytest_asyncio.fixture(scope='session')
async def user_wo_permissions_headers(user_wo_permissions: User) -> dict[str, str]:
    return __create_headers(user_wo_permissions)


@pytest_asyncio.fixture(scope='session')
async def user_superuser_headers(user_superuser: User) -> dict[str, str]:
    return __create_headers(user_superuser)


def __create_headers(user: User) -> dict[str, str]:
    aud = ['fastapi-users:auth'] + list(user.permissions) + (['*:*'] if user.is_superuser else [])
    data = {'sub': str(user.id), 'aud': aud}
    token = generate_jwt(data, Settings().service_secret, 3600, algorithm='HS256')
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def http_client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=app.app), base_url="http://127.0.0.1:8000")


@pytest_asyncio.fixture(scope='session')
async def user_db() -> BeanieUserDatabase[User]:
    return await get_user_db().__anext__()


@pytest_asyncio.fixture(scope='session')
async def menu_db() -> BeanieWeekMenuDatabase:
    return await get_menu_db().__anext__()


@pytest_asyncio.fixture(scope='session')
async def user_manager(user_db) -> BaseUserManager[User, UUID]:
    return await get_user_manager(user_db).__anext__()


@pytest_asyncio.fixture(scope='session')
async def week_menu_manager(menu_db) -> BeanieWeekMenuDatabase:
    return await get_week_menu_manager(menu_db).__anext__()
