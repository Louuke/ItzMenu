from functools import lru_cache

from itzmenu_service.config.settings import Settings
from itzmenu_service.persistence.models import User
from fastapi_users_db_beanie import BeanieUserDatabase
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient, AsyncIOMotorGridFSBucket


@lru_cache
def db() -> AsyncIOMotorDatabase:
    settings = Settings()
    return AsyncIOMotorClient(settings.mongo_db_url)[settings.mongo_db_name]


@lru_cache
def fs() -> AsyncIOMotorGridFSBucket:
    return AsyncIOMotorGridFSBucket(db())


async def get_user_db() -> BeanieUserDatabase[User]:
    yield BeanieUserDatabase(User)
