import pytest
from fastapi import HTTPException
from itzmenu_service.routes.permissions import PermissionChecker
from itzmenu_service.persistence.models import User


def test_permission_checker_with_required_permissions_and_user_has_them():
    checker = PermissionChecker(["read", "write"])
    user = User(permissions=["read", "write", "delete"], email='email@example.org', hashed_password='pwd')
    assert checker(user)


def test_permission_checker_with_required_permissions_and_user_does_not_have_them():
    checker = PermissionChecker(["read", "write"])
    user = User(permissions=["read"], email='email@example.org', hashed_password='pwd')
    with pytest.raises(HTTPException):
        checker(user)


def test_permission_checker_with_required_permissions_and_user_is_superuser():
    checker = PermissionChecker(["read", "write"])
    user = User(permissions=["read"], email='email@example.org', hashed_password='pwd', is_superuser=True)
    assert checker(user)


def test_permission_checker_with_no_required_permissions_and_user_has_no_permissions():
    checker = PermissionChecker([])
    user = User(permissions=[], email='email@example.org', hashed_password='pwd', is_superuser=False)
    assert checker(user)


def test_permission_checker_with_no_required_permissions_and_user_is_superuser():
    checker = PermissionChecker([])
    user = User(permissions=["read"], email='email@example.org', hashed_password='pwd', is_superuser=True)
    assert checker(user)
