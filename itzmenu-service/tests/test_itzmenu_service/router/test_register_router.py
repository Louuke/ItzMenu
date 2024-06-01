import pytest
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer

from itzmenu_service.persistence.models import User


@pytest.mark.asyncio(scope='session')
class TestRegisterRouter:

    test_user_1_email = 'test_register_1@example.org'
    test_user_2_email = 'test_register_2@example.org'
    test_user_password = 'paSSw0rd'

    async def test_auth_register(self, http_client: AsyncClient):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            valid_register_data = {'email': self.test_user_1_email, 'password': self.test_user_password}
            response = await http_client.post('/auth/register', json=valid_register_data)
            assert response.status_code == 201
            user = response.json()
            assert user['email'] == self.test_user_1_email
            assert user['is_active']
            assert user['permissions'] == []
            assert len(srv.messages) == 1

    async def test_auth_register_duplicate(self, http_client: AsyncClient, user_w_permissions: User):
        data = {'email': user_w_permissions.email, 'password': 'password'}
        response = await http_client.post('/auth/register', json=data)
        assert response.status_code == 400

    async def test_auth_register_invalid_email(self, http_client: AsyncClient):
        data = {'email': 'invalid', 'password': '43sfSDpez#3'}
        response = await http_client.post('/auth/register', json=data)
        assert response.status_code == 422

    async def test_auth_register_invalid_password(self, http_client: AsyncClient):
        data = {'email': 'valid@example.org', 'password': 'sho'}
        response = await http_client.post('/auth/register', json=data)
        assert response.status_code == 400

    async def test_auth_register_excluded_fields(self, http_client: AsyncClient):
        with SmtpMockServer('127.0.0.1', 42000):
            data = {'email': self.test_user_2_email, 'password': self.test_user_password, 'id': 'id',
                    'is_active': False, 'is_superuser': True, 'is_verified': True, 'permissions': ['read']}
            response = await http_client.post('/auth/register', json=data)
            assert response.status_code == 201
            user = response.json()
            assert user['id'] != 'id'
            assert not user['is_superuser']
            assert not user['is_verified']
            assert user['is_active']
            assert user['permissions'] == []
