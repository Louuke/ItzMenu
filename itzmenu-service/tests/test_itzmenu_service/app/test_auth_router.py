import pytest
from beanie import PydanticObjectId
from fastapi_users import BaseUserManager
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer

from itzmenu_service.persistence.models import User
from itzmenu_api.persistence.schemas import UserCreate, UserUpdate


@pytest.mark.asyncio(scope='session')
class TestAuthRouter:
    TEST_USER_EMAIL = 'test_auth_1@example.org'
    TEST_USER_EMAIL_2 = 'test_auth_2@example.org'
    TEST_USER_PASSWORD = 'paSSw0rd'

    async def test_auth_login(self, http_client: AsyncClient, user_manager: BaseUserManager[User, PydanticObjectId]):
        with SmtpMockServer('127.0.0.1', 42000):
            user = UserCreate(email=self.TEST_USER_EMAIL, password=self.TEST_USER_PASSWORD)
            result = await user_manager.create(user)
            assert result.email == self.TEST_USER_EMAIL
            data = {'username': self.TEST_USER_EMAIL, 'password': self.TEST_USER_PASSWORD}
            response = await http_client.post('/auth/login', data=data)
            json = response.json()
            assert response.status_code == 200
            assert len(json['access_token']) > 0
            assert json['token_type'] == 'bearer'

    async def test_auth_login_invalid_credentials(self, http_client: AsyncClient):
        data = {'username': self.TEST_USER_EMAIL, 'password': 'invalid'}
        response = await http_client.post('/auth/login', data=data)
        assert response.status_code == 400

    async def test_auth_login_inactive_user(self, http_client: AsyncClient,
                                            user_manager: BaseUserManager[User, PydanticObjectId]):
        with SmtpMockServer('127.0.0.1', 42000):
            user = UserCreate(email=self.TEST_USER_EMAIL_2, password=self.TEST_USER_PASSWORD)
            result = await user_manager.create(user)
            update = UserUpdate(is_active=False)
            await user_manager.update(update, result)
            data = {'username': self.TEST_USER_EMAIL_2, 'password': self.TEST_USER_PASSWORD}
            response = await http_client.post('/auth/login', data=data)
            assert response.status_code == 400
