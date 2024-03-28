from functools import lru_cache

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from itz_menu import utils
from itz_menu.config.settings import Settings
from itz_menu.persistence.models import WeekMenu

settings = Settings()


@lru_cache()
def client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.mongo_db_url)


@lru_cache()
def fs() -> AsyncIOMotorGridFSBucket:
    return AsyncIOMotorGridFSBucket(client()[settings.mongo_db_name])


async def init():
    database_name = settings.mongo_db_test_name if utils.is_test_running() else settings.mongo_db_name
    await init_beanie(database=client()[database_name], document_models=[WeekMenu])
