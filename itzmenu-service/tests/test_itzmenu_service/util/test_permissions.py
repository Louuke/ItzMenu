import pytest
from unittest.mock import Mock
from fastapi import HTTPException
from itzmenu_service.util.permissions import PermissionChecker
from itzmenu_service.authentication.strategy.jwt import JWTPermissionStrategy


@pytest.fixture
def strategy():
    return JWTPermissionStrategy(secret='secret', lifetime_seconds=3600)


def test_permission_checker_with_sufficient_permissions(strategy: JWTPermissionStrategy):
    request = Mock()
    request.headers.get.return_value = 'Bearer token'
    strategy.get_permissions = Mock(return_value=['read:menu', 'write:menu'])
    checker = PermissionChecker(required_permissions=['read:menu'])
    assert checker(request, strategy) is True


def test_permission_checker_with_insufficient_permissions(strategy: JWTPermissionStrategy):
    request = Mock()
    request.headers.get.return_value = 'Bearer token'
    strategy.get_permissions = Mock(return_value=['read:menu'])
    checker = PermissionChecker(required_permissions=['write:menu'])
    with pytest.raises(HTTPException) as excinfo:
        checker(request, strategy)
    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == 'User has insufficient permissions'


def test_permission_checker_with_missing_authorization_header(strategy: JWTPermissionStrategy):
    request = Mock()
    request.headers.get.return_value = None
    checker = PermissionChecker(required_permissions=['read:menu'])
    with pytest.raises(HTTPException) as excinfo:
        checker(request, strategy)
    assert excinfo.value.status_code == 401
    assert excinfo.value.detail == 'Authorization header is missing'


def test_permission_checker_with_all_permissions(strategy: JWTPermissionStrategy):
    request = Mock()
    request.headers.get.return_value = 'Bearer token'
    strategy.get_permissions = Mock(return_value=['*:*'])
    checker = PermissionChecker(required_permissions=['read:menu', 'write:menu'])
    assert checker(request, strategy) is True
