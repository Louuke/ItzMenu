import pytest
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer

from itzmenu_service.persistence.models import User


@pytest.mark.asyncio(scope='session')
class TestAuthRouter:

    async def test_auth_login(self, http_client: AsyncClient, user_w_permissions: User, user_pwd: str):
        with SmtpMockServer('127.0.0.1', 42000):
            data = {'username': user_w_permissions.email, 'password': user_pwd}
            response = await http_client.post('/auth/login', data=data)
            json = response.json()
            assert response.status_code == 200
            assert len(json['access_token']) > 0
            assert json['token_type'] == 'bearer'

    async def test_auth_login_invalid_credentials(self, http_client: AsyncClient, user_w_permissions: User):
        data = {'username': user_w_permissions.email, 'password': 'invalid'}
        response = await http_client.post('/auth/login', data=data)
        assert response.status_code == 400

    async def test_auth_login_inactive_user(self, http_client: AsyncClient, user_inactive: User, user_pwd: str):
        with SmtpMockServer('127.0.0.1', 42000):
            data = {'username': user_inactive.email, 'password': user_pwd}
            response = await http_client.post('/auth/login', data=data)
            assert response.status_code == 400
