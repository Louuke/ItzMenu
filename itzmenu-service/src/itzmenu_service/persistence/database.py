from functools import lru_cache

from itzmenu_service.config.settings import Settings
from itzmenu_service.persistence.adapter.adapter import BeanieWeekMenuDatabase
from itzmenu_service.persistence.models import User, WeekMenu
from fastapi_users_db_beanie import BeanieUserDatabase
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient, AsyncIOMotorGridFSBucket


@lru_cache
def db() -> AsyncIOMotorDatabase:
    settings = Settings()
    return AsyncIOMotorClient(settings.mongodb_url)[settings.mongodb_name]


@lru_cache
def fs() -> AsyncIOMotorGridFSBucket:
    return AsyncIOMotorGridFSBucket(db())


async def get_user_db() -> BeanieUserDatabase[User]:
    yield BeanieUserDatabase(User)


async def get_menu_db() -> BeanieWeekMenuDatabase:
    yield BeanieWeekMenuDatabase(WeekMenu)
