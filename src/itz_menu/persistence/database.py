import gridfs
from bunnet import init_bunnet
from pymongo import MongoClient

from itz_menu import utils
from itz_menu.config.settings import Settings
from itz_menu.persistence.models import *

fs: gridfs.GridFS | None = None


def init(settings: Settings = Settings()):
    client = MongoClient(settings.mongo_db_url)
    global fs
    fs = gridfs.GridFS(client[settings.mongo_db_name])
    database_name = settings.mongo_db_test_name if utils.is_test_running() else settings.mongo_db_name
    init_bunnet(database=client[database_name], document_models=[WeekMenu])
