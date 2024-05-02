import logging as log
from io import BytesIO

import itzmenu.ocr.extractor as extractor
import itzmenu.ocr.postprocess as postprocess
import itzmenu.persistence.database as database
import itzmenu.utils as utils
from itzmenu.persistence.models import WeekMenu
from itzmenu.rest.client import MenuClient
from itzmenu.config.settings import Settings


__client = MenuClient()


async def fetch_menu():
    if (menu := __client.get_week_menu()) is None:
        return
    log.info(f'Received menu with {len(menu)} bytes')
    await process_image(menu)


async def process_image(image: bytes):
    filename = f'{utils.bytes_to_sha256(image)}.jpg'
    if await WeekMenu.find(WeekMenu.filename == filename).first_or_none() is not None:
        log.info(f'Menu with checksum {filename} already exists')
        return
    if (p := extractor.period_of_validity(image)) is None or (df := extractor.img_to_dataframe(image)) is None:
        log.warning(f'Failed to extract menu from image')
        return
    log.info(f'Extracted dataframe with {df.shape[0]} rows and {df.shape[1]} columns')
    log.info(f'Extracted time period: {utils.timestamp_to_date(p[0])} - {utils.timestamp_to_date(p[1])}')
    await postprocess.dataframe_to_week_menu(df, p, filename).insert()
    if Settings().ocr_save_images:
        await database.fs().upload_from_stream(filename, BytesIO(image))
    log.info(f'Inserted menu with filename {filename}')
