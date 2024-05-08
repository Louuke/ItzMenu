from functools import lru_cache

from itzmenu_service.config.settings import Settings
from itzmenu_service.persistence.models import User
from fastapi_users_db_beanie import BeanieUserDatabase
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from itzmenu_service.util import env


@lru_cache
def db() -> AsyncIOMotorDatabase:
    settings = Settings()
    database_name = settings.mongo_db_test_name if env.is_running_tests() else settings.mongo_db_name
    return AsyncIOMotorClient(settings.mongo_db_url)[database_name]


@lru_cache
def fs() -> AsyncIOMotorGridFSBucket:
    return AsyncIOMotorGridFSBucket(db())


async def get_user_db() -> BeanieUserDatabase[User]:
    yield BeanieUserDatabase(User)
