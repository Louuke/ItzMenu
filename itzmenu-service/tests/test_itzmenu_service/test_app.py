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

    @pytest.mark.dependency(depends=["test_auth_register"])
    async def test_auth_login(self, http_client):
        print('test_auth_login')


@pytest.mark.asyncio
async def test_read_main(user_manager):
    user = await user_manager.get_by_email('fastapi@jannsen.org')
    print(user)


@pytest.mark.asyncio
async def test_read_main2(http_client):
    response = await http_client.post('/auth/login', data={"username": "fastapi@jannsen.org", "password": "password"})
    print(response.json())
