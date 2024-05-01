import logging as log

import itzmenu.persistence.database as database
from itzmenu.config.settings import Settings

__version__ = '0.0.1'
settings = Settings()

log.basicConfig(level=log.getLevelName(settings.log_level), format='%(asctime)s - %(levelname)s - %(message)s')
log.info(f'Running with settings: {settings}')
