import asyncio
import os
import logging as log
import sys

from itz_menu.persistence import database
from itz_menu.cmd import Parser


async def main():
    await database.init()
    await Parser(sys.argv).execute()
    log.info('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))
    while True:
        await asyncio.sleep(1000)

if __name__ == '__main__':
    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
