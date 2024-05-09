import pytest
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer


@pytest.mark.asyncio(scope='session')
class TestRegisterRouter:

    TEST_USER_EMAIL = 'test_register_1@example.org'
    TEST_USER_2_EMAIL = 'test_register_2@example.org'
    TEST_USER_PASSWORD = 'paSSw0rd'
    VALID_REGISTER_DATA = {'email': TEST_USER_EMAIL, 'password': TEST_USER_PASSWORD}

    @pytest.mark.dependency()
    async def test_auth_register(self, http_client: AsyncClient):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            response = await http_client.post('/auth/register', json=self.VALID_REGISTER_DATA)
            assert response.status_code == 201
            user = response.json()
            assert user['email'] == self.TEST_USER_EMAIL
            assert user['is_active']
            assert user['permissions'] == []
            assert len(srv.messages) == 1

    @pytest.mark.dependency(depends=['TestRegisterRouter::test_auth_register'])
    async def test_auth_register_duplicate(self, http_client: AsyncClient):
        response = await http_client.post('/auth/register', json=self.VALID_REGISTER_DATA)
        assert response.status_code == 400

    async def test_auth_register_invalid_email(self, http_client: AsyncClient):
        data = {'email': 'invalid', 'password': self.TEST_USER_PASSWORD}
        response = await http_client.post('/auth/register', json=data)
        assert response.status_code == 422

    async def test_auth_register_invalid_password(self, http_client: AsyncClient):
        data = {'email': 'valid@example.org', 'password': 'sho'}
        response = await http_client.post('/auth/register', json=data)
        assert response.status_code == 400

    async def test_auth_register_excluded_fields(self, http_client: AsyncClient):
        with SmtpMockServer('127.0.0.1', 42000):
            data = {'email': self.TEST_USER_2_EMAIL, 'password': self.TEST_USER_PASSWORD, 'id': 'id', 'is_active': True,
                    'is_superuser': True, 'is_verified': True, 'permissions': ['read']}
            response = await http_client.post('/auth/register', json=data)
            assert response.status_code == 201
            user = response.json()
            assert user['id'] != 'id'
            assert not user['is_superuser']
            assert not user['is_verified']
            assert user['permissions'] == []

    @pytest.mark.dependency(depends=['TestAppAuth::test_auth_register'])
    @pytest.mark.skip
    async def test_auth_request_verify(self, http_client: AsyncClient):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            data = {'username': self.TEST_USER_EMAIL, 'password': self.TEST_USER_PASSWORD}
            response = await http_client.post('/auth/login', data=data)
            auth = response.json()['access_token']
            headers = {'Authorization': f'Bearer {auth}'}
            data = {'email': self.TEST_USER_EMAIL}
            response = await http_client.post('/auth/request-verify-token', json=data, headers=headers)
            assert response.status_code == 202
            assert len(srv.messages) == 1

    @pytest.mark.dependency(depends=['TestAppAuth::test_auth_register'])
    @pytest.mark.skip
    async def test_auth_forgot_password(self, http_client: AsyncClient):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            data = {'email': self.TEST_USER_EMAIL}
            response = await http_client.post('/auth/forgot-password', json=data)
            assert response.status_code == 202
            assert len(srv.messages) == 1
