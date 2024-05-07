from fastapi import Depends, HTTPException

from itzmenu_service.manager.users import current_active_user
from itzmenu_service.persistence.models import User


class PermissionChecker:

    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    def __call__(self, user: User = Depends(current_active_user)):
        if not set(self.required_permissions).issubset(user.permissions):
            raise HTTPException(status_code=403, detail='User has insufficient permissions')
        return user
