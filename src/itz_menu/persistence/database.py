import sys

from bunnet import init_bunnet
from pymongo import MongoClient

from itz_menu.config.settings import Settings
from itz_menu.persistence.models import *


def init(settings: Settings):
    client = MongoClient(settings.mongo_db_url)
    database_name = settings.mongo_db_test_name if is_test_running() else settings.mongo_db_name
    init_bunnet(database=client[database_name], document_models=[WeekMenu])


def is_test_running():
    return 'pytest' in sys.modules or 'unittest' in sys.modules
