from functools import lru_cache

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from itzmenu_extractor.config.settings import Settings
from itzmenu_extractor.persistence.models import WeekMenu
import itzmenu_extractor.util.env as env

settings = Settings()


@lru_cache()
def client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.mongo_db_url)


@lru_cache()
def fs() -> AsyncIOMotorGridFSBucket:
    return AsyncIOMotorGridFSBucket(client()[settings.mongo_db_name])


async def init():
    database_name = settings.mongo_db_test_name if env.is_running_tests() else settings.mongo_db_name
    await init_beanie(database=client()[database_name], document_models=[WeekMenu])
