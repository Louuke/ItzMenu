import logging as log
import itz_menu.persistence.database as database
from itz_menu.config.settings import Settings
from itz_menu.services import UpdateMenuService

__version__ = '0.0.1'
settings = Settings()
log.basicConfig(level=log.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

database.init(settings)

