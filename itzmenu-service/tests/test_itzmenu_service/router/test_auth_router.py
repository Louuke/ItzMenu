import pytest
from fastapi_users.password import PasswordHelper
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer

from itzmenu_service.persistence.models import User


@pytest.mark.asyncio(scope='session')
class TestAuthRouter:
    TEST_USER_EMAIL = 'test_auth_1@example.org'
    TEST_USER_EMAIL_2 = 'test_auth_2@example.org'
    TEST_USER_PASSWORD = 'paSSw0rd'
    TEST_USER_HASHED_PASSWORD = PasswordHelper().hash(TEST_USER_PASSWORD)

    async def test_auth_login(self, http_client: AsyncClient):
        with SmtpMockServer('127.0.0.1', 42000):
            result = await User(email=self.TEST_USER_EMAIL, hashed_password=self.TEST_USER_HASHED_PASSWORD).create()
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

    async def test_auth_login_inactive_user(self, http_client: AsyncClient):
        with SmtpMockServer('127.0.0.1', 42000):
            result = await User(email=self.TEST_USER_EMAIL_2, hashed_password=self.TEST_USER_HASHED_PASSWORD).create()
            user = await User.find_one(User.id == result.id)
            user.is_active = False
            await user.save()
            data = {'username': self.TEST_USER_EMAIL_2, 'password': self.TEST_USER_PASSWORD}
            response = await http_client.post('/auth/login', data=data)
            assert response.status_code == 400
