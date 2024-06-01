import pytest
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer

from itzmenu_service.persistence.models import User


@pytest.mark.asyncio(scope='session')
class TestResetPasswordRouter:

    async def test_auth_forgot_password(self, http_client: AsyncClient, user_w_permissions: User):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            response = await http_client.post('/auth/forgot-password', json={'email': user_w_permissions.email})
            assert response.status_code == 202
            assert len(srv.messages) == 1
