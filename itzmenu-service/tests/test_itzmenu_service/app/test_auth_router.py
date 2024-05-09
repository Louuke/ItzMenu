import pytest
from beanie import PydanticObjectId
from fastapi_users import BaseUserManager
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer

from itzmenu_service.persistence.models import User
from itzmenu_service.persistence.schemas import UserCreate


@pytest.mark.asyncio(scope='session')
class TestAuthRouter:
    TEST_USER_EMAIL = 'test_auth_1@example.org'
    TEST_USER_PASSWORD = 'paSSw0rd'

    async def test_auth_login(self, http_client: AsyncClient, user_manager: BaseUserManager[User, PydanticObjectId]):
        with SmtpMockServer('127.0.0.1', 42000):
            user = UserCreate(email=self.TEST_USER_EMAIL, password=self.TEST_USER_PASSWORD)
            result = await user_manager.create(user)
            assert result.email == self.TEST_USER_EMAIL
            data = {'username': self.TEST_USER_EMAIL, 'password': self.TEST_USER_PASSWORD}
            response = await http_client.post('/auth/login', data=data)
            assert response.status_code == 200
