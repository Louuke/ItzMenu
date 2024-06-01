import json

import pytest
from fastapi_users.password import PasswordHelper
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer

from itzmenu_service.manager.users import auth_backend
from itzmenu_service.persistence.models import User


@pytest.mark.asyncio(scope='session')
class TestVerifyRouter:

    TEST_USER_EMAIL = 'test_verify_1@example.org'
    TEST_USER_PASSWORD = 'paSSw0rd'
    TEST_USER_HASHED_PASSWORD = PasswordHelper().hash(TEST_USER_PASSWORD)

    async def test_auth_request_verify(self, http_client: AsyncClient):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            user = await User(email=self.TEST_USER_EMAIL, hashed_password=self.TEST_USER_HASHED_PASSWORD).create()
            result = await auth_backend.login(auth_backend.get_strategy(), user)
            response = json.loads(result.body.decode('utf-8'))
            headers = {'Authorization': f'Bearer {response["access_token"]}'}
            data = {'email': self.TEST_USER_EMAIL}
            response = await http_client.post('/auth/request-verify-token', json=data, headers=headers)
            assert response.status_code == 202
            assert len(srv.messages) == 1
