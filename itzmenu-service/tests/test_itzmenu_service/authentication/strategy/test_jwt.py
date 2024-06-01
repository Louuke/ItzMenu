from unittest.mock import Mock

import pytest
from jwt import DecodeError

from itzmenu_service.authentication.strategy.jwt import JWTPermissionStrategy


@pytest.fixture
def strategy():
    return JWTPermissionStrategy(secret='secret', lifetime_seconds=3600)


@pytest.mark.asyncio(scope='session')
class TestJWTPermissionStrategy:

    async def test_jwt_strategy_generates_token_with_correct_audience(self, strategy: JWTPermissionStrategy):
        user = Mock()
        user.id = '123'
        user.permissions = ['read:menu']
        user.is_superuser = False
        token = f'Bearer {await strategy.write_token(user)}'
        permissions = strategy.get_permissions(token)
        assert permissions == ['fastapi-users:auth', 'read:menu']

    async def test_jwt_strategy_generates_token_for_superuser(self, strategy: JWTPermissionStrategy):
        user = Mock()
        user.id = '123'
        user.permissions = ['read:menu']
        user.is_superuser = True
        token = f'Bearer {await strategy.write_token(user)}'
        permissions = strategy.get_permissions(token)
        assert permissions == ['fastapi-users:auth', 'read:menu', '*:*']

    async def test_jwt_strategy_gets_permissions_from_token(self, strategy: JWTPermissionStrategy):
        user = Mock()
        user.id = '123'
        user.permissions = ['read:menu']
        user.is_superuser = False
        token = f'Bearer {await strategy.write_token(user)}'
        permissions = strategy.get_permissions(token)
        assert permissions == ['fastapi-users:auth', 'read:menu']

    def test_jwt_strategy_returns_empty_permissions_for_invalid_token(self, strategy: JWTPermissionStrategy):
        with pytest.raises(DecodeError):
            strategy.get_permissions('invalid_token')
