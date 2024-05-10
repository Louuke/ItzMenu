import pytest
from beanie import PydanticObjectId
from fastapi_users import BaseUserManager
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer

from itzmenu_service.persistence.models import User
from itzmenu_service.persistence.schemas import UserCreate


@pytest.mark.asyncio(scope='session')
class TestResetPasswordRouter:

    TEST_USER_EMAIL = 'test_reset_1@example.org'
    TEST_USER_PASSWORD = 'paSSw0rd'

    async def test_auth_forgot_password(self, http_client: AsyncClient,
                                        user_manager: BaseUserManager[User, PydanticObjectId]):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            user = UserCreate(email=self.TEST_USER_EMAIL, password=self.TEST_USER_PASSWORD)
            await user_manager.create(user)
            response = await http_client.post('/auth/forgot-password', json={'email': self.TEST_USER_EMAIL})
            assert response.status_code == 202
            assert len(srv.messages) == 2
