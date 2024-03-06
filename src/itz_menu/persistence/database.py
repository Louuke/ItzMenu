from bunnet import init_bunnet
from pymongo import MongoClient

from itz_menu.config.settings import Settings
from itz_menu.persistence.models import *


def init():
    settings = Settings()
    client = MongoClient(settings.mongo_db_url)
    init_bunnet(database=client[settings.mongo_db_name], document_models=[WeekMenu])
