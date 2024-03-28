import asyncio
import datetime
import os
import sys
import re
import logging as log

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import itz_menu.jobs as jobs
import itz_menu.utils as utils
from itz_menu.persistence import database


async def main():
    await database.init()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(jobs.fetch_menu, 'interval', seconds=3600, max_instances=1, next_run_time=datetime.datetime.now())
    scheduler.start()
    log.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    while True:
        await asyncio.sleep(1000)

if len(sys.argv) == 1:
    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
elif all(re.match(r'^[a-zA-Z0-9/_-]+\.jpg$', filename) for filename in sys.argv[1:]):
    images = [utils.load_image(filename) for filename in sys.argv[1:]]
    [jobs.process_image(image) for image in images]
else:
    log.warning(f'Invalid arguments: {sys.argv}')
    log.warning('Usage: itz_menu [filename.jpg ...]')
