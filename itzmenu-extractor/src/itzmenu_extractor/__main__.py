import asyncio
import os
import logging as log
import sys

from itzmenu_extractor.persistence import database
from itzmenu_extractor.cmd import Parser

__running = True


async def main():
    await database.init()
    await Parser(sys.argv).execute()
    log.info(f'Press Ctrl+{"Break" if os.name == "nt" else "C"} to exit')
    while __running:
        await asyncio.sleep(1000)

if __name__ == '__main__':
    # Execution will block here until Ctrl+C (Ctrl+Break on Windows) is pressed.
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        __running = False
