import sys
import re
import logging as log

from itz_menu.services import UpdateMenuService
from itz_menu.utils import load_image


service = UpdateMenuService()

if len(sys.argv) == 1:
    service.start()
    service.join()
elif all(re.match(r'^[a-zA-Z0-9/_-]+\.jpg$', filename) for filename in sys.argv[1:]):
    images = [load_image(filename) for filename in sys.argv[1:]]
    [service.process_image(image) for image in images]
else:
    log.warning(f'Invalid arguments: {sys.argv}')
    log.warning('Usage: itz_menu [filename.jpg ...]')
