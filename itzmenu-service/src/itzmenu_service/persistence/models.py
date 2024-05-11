from uuid import UUID, uuid4

from beanie import Document
from fastapi_users.db import BeanieBaseUser
from pydantic import Field


class User(BeanieBaseUser, Document):
    id: UUID = Field(default_factory=uuid4)
    permissions: set[str] = []

    class Settings(BeanieBaseUser.Settings):
        name = 'users'
