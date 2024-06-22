from fastapi import Depends, Request, HTTPException

from itzmenu_service.authentication.strategy.jwt import JWTPermissionStrategy
from itzmenu_service.manager.users import get_jwt_strategy


class PermissionChecker:

    def __init__(self, required_permissions: list[str]):
        self.required_permissions = required_permissions

    def __call__(self, request: Request, strategy: JWTPermissionStrategy = Depends(get_jwt_strategy)):
        if (authorization := request.headers.get('Authorization')) is None:
            raise HTTPException(status_code=401, detail='Authorization header is missing')
        if (permissions := strategy.get_permissions(authorization)) is None:
            raise HTTPException(status_code=401, detail='Invalid token')
        if set(self.required_permissions).issubset(permissions) or '*:*' in permissions:
            return True
        raise HTTPException(status_code=403, detail='User has insufficient permissions')
