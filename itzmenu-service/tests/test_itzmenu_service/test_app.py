import pytest
from smtp_test_server.context import SmtpMockServer


@pytest.mark.asyncio
class TestAppAuth:

    TEST_USER_EMAIL = 'test_auth@example.org'
    TEST_USER_PASSWORD = 'password'

    async def test_auth_register(self, http_client):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            data = {'email': self.TEST_USER_EMAIL, 'password': self.TEST_USER_PASSWORD}
            response = await http_client.post('/auth/register', json=data)
            assert response.status_code == 201
            user = response.json()
            assert user['email'] == self.TEST_USER_EMAIL
            assert user['is_active']
            assert len(srv.messages) == 1

    @pytest.mark.dependency(depends=['TestAppAuth.test_auth_register'])
    async def test_auth_login(self, http_client):
        data = {'username': self.TEST_USER_EMAIL, 'password': self.TEST_USER_PASSWORD}
        response = await http_client.post('/auth/login', data=data)
        assert response.status_code == 200
        json = response.json()
        assert len(json['access_token']) > 0
        assert json['token_type'] == 'bearer'

    @pytest.mark.dependency(depends=['TestAppAuth.test_auth_register'])
    async def test_auth_request_verify(self, http_client):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            data = {'username': self.TEST_USER_EMAIL, 'password': self.TEST_USER_PASSWORD}
            response = await http_client.post('/auth/login', data=data)
            auth = response.json()['access_token']
            headers = {'Authorization': f'Bearer {auth}'}
            data = {'email': self.TEST_USER_EMAIL}
            response = await http_client.post('/auth/request-verify-token', json=data, headers=headers)
            assert response.status_code == 202
            assert len(srv.messages) == 1

    @pytest.mark.dependency(depends=['TestAppAuth.test_auth_register'])
    async def test_auth_forgot_password(self, http_client):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            data = {'email': self.TEST_USER_EMAIL}
            response = await http_client.post('/auth/forgot-password', json=data)
            assert response.status_code == 202
            assert len(srv.messages) == 1


@pytest.mark.asyncio
async def test_read_main(user_manager):
    user = await user_manager.get_by_email('fastapi@jannsen.org')
    print(user)


@pytest.mark.asyncio
async def test_read_main2(http_client):
    response = await http_client.post('/auth/login', data={"username": "fastapi@jannsen.org", "password": "password"})
    print(response.json())
