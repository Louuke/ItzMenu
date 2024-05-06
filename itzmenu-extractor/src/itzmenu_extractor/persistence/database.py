from functools import lru_cache

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from itzmenu_extractor.config.settings import Settings
from itzmenu_extractor.persistence.models import WeekMenu
import itzmenu_extractor.util.env as env

settings = Settings()


@lru_cache()
def db() -> AsyncIOMotorDatabase:
    database_name = settings.mongo_db_test_name if env.is_running_tests() else settings.mongo_db_name
    return AsyncIOMotorClient(settings.mongo_db_url)[database_name]


@lru_cache()
def fs() -> AsyncIOMotorGridFSBucket:
    return AsyncIOMotorGridFSBucket(db())


async def init():
    await init_beanie(database=db(), document_models=[WeekMenu])
