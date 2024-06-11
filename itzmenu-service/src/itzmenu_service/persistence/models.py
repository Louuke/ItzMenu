import time
from uuid import UUID, uuid4

from beanie import Document, Indexed
from fastapi_users.db import BeanieBaseUser
from pydantic import Field

from itzmenu_api.persistence.schemas import DayMenu


class User(BeanieBaseUser, Document):
    id: UUID = Field(default_factory=uuid4)
    permissions: set[str] = []

    class Settings(BeanieBaseUser.Settings):
        name = 'users'


class WeekMenu(Document):
    id: UUID = Field(default_factory=uuid4)
    start_timestamp: Indexed(int) = Field(ge=0)
    end_timestamp: Indexed(int) = Field(ge=1)
    created_at: int = Field(default_factory=lambda: int(time.time()), ge=0)
    img_checksum: Indexed(str, unique=True) = Field(pattern=r'^[a-f0-9]{32}$')
    img: str = Field(pattern=r'^[a-zA-Z0-9+/]+={0,2}$')
    menus: list[DayMenu] = Field(default=[])

    class Settings:
        name = 'week_menus'
