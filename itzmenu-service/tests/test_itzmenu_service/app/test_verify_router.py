import json

import pytest
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer

from itzmenu_service.manager.users import auth_backend
from itzmenu_service.persistence.schemas import UserCreate


@pytest.mark.asyncio(scope='session')
class TestVerifyRouter:

    TEST_USER_EMAIL = 'test_verify_1@example.org'
    TEST_USER_PASSWORD = 'paSSw0rd'

    async def test_auth_request_verify(self, http_client: AsyncClient, user_manager):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            user = UserCreate(email=self.TEST_USER_EMAIL, password=self.TEST_USER_PASSWORD)
            user = await user_manager.create(user)
            result = await auth_backend.login(auth_backend.get_strategy(), user)
            response = json.loads(result.body.decode('utf-8'))
            headers = {'Authorization': f'Bearer {response["access_token"]}'}
            data = {'email': self.TEST_USER_EMAIL}
            response = await http_client.post('/auth/request-verify-token', json=data, headers=headers)
            assert response.status_code == 202
            assert len(srv.messages) == 2
