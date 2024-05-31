import logging as log
import re
from typing import Optional, Union
from uuid import UUID

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, schemas, models, InvalidPasswordException, UUIDIDMixin
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.db import BeanieUserDatabase

from itzmenu_service.authentication.strategy.jwt import JWTPermissionStrategy
from itzmenu_service.persistence.database import User, get_user_db
from itzmenu_service.mail import client
from itzmenu_service.config.settings import settings


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    reset_password_token_secret = settings.service_secret
    verification_token_secret = settings.service_secret

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        log.debug(f'User {user.id} has registered.')
        await self.request_verify(user)

    async def on_after_forgot_password(self, user: User, token: str, request: Optional[Request] = None):
        log.debug(f'User {user.id} has forgot their password. Reset token: {token}')
        client.send_reset_password_email(user.email, token)

    async def on_after_request_verify(self, user: User, token: str, request: Optional[Request] = None):
        log.debug(f'Verification requested for user {user.id}. Verification token: {token}')
        client.send_verification_email(user.email, token)

    async def validate_password(self, password: str, user: Union[schemas.UC, models.UP]) -> None:
        # Custom password validation
        if len(password) < 8:
            raise InvalidPasswordException("Password should be at least 8 characters long")
        if not re.search('[a-z]', password):
            raise InvalidPasswordException("Password should contain at least one lowercase letter")
        if not re.search('[A-Z]', password):
            raise InvalidPasswordException("Password should contain at least one uppercase letter")
        if not re.search('[0-9]', password):
            raise InvalidPasswordException("Password should contain at least one number")


async def get_user_manager(user_db: BeanieUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTPermissionStrategy(secret=settings.service_secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, UUID](get_user_manager, [auth_backend])

current_active_user = fastapi_users.current_user(active=True)
