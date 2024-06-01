from uuid import UUID

import pytest
from fastapi_users import BaseUserManager
from fastapi_users.password import PasswordHelper
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer

from itzmenu_service.persistence.models import User


@pytest.mark.asyncio(scope='session')
class TestResetPasswordRouter:

    TEST_USER_EMAIL = 'test_reset_1@example.org'
    TEST_USER_PASSWORD = 'paSSw0rd'
    TEST_USER_HASHED_PASSWORD = PasswordHelper().hash(TEST_USER_PASSWORD)

    async def test_auth_forgot_password(self, http_client: AsyncClient):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            await User(email=self.TEST_USER_EMAIL, hashed_password=self.TEST_USER_HASHED_PASSWORD).create()
            response = await http_client.post('/auth/forgot-password', json={'email': self.TEST_USER_EMAIL})
            assert response.status_code == 202
            assert len(srv.messages) == 1
