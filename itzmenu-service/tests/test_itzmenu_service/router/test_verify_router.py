import pytest
from httpx import AsyncClient
from smtp_test_server.context import SmtpMockServer

from itzmenu_service.persistence.models import User


@pytest.mark.asyncio(scope='session')
class TestVerifyRouter:

    async def test_auth_request_verify(self, http_client: AsyncClient, user_w_permissions: User,
                                       user_w_permissions_headers: str):
        with SmtpMockServer('127.0.0.1', 42000) as srv:
            headers = {'Authorization': f'Bearer {user_w_permissions_headers}'}
            data = {'email': user_w_permissions.email}
            response = await http_client.post('/auth/request-verify-token', json=data, headers=headers)
            assert response.status_code == 202
            assert len(srv.messages) == 1
