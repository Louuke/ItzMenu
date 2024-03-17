import logging as log
import threading
import time

import itz_menu.ocr.extractor as extractor
import itz_menu.ocr.postprocess as postprocess
import itz_menu.persistence.database as database
import itz_menu.utils as utils
from itz_menu.persistence.models import WeekMenu
from itz_menu.rest.client import MenuClient
from itz_menu.config.settings import Settings


class UpdateMenuService(threading.Thread):

    def __init__(self, settings: Settings = Settings()):
        super().__init__()
        self.__client = MenuClient()
        self.__settings = settings
        self.__running = False

    def start(self):
        if self.__running:
            return
        self.__running = True
        super().start()

    def stop(self):
        self.__running = False

    def run(self):
        first_run = True
        while self.__running:
            time.sleep(0 if first_run else self.__settings.ocr_check_interval)
            first_run = False
            if (menu := self.__client.get_week_menu()) is None:
                continue
            log.info(f'Received menu with {len(menu)} bytes')
            self.process_image(menu)

    def process_image(self, image: bytes):
        filename = f'{utils.bytes_to_sha256(image)}.jpg'
        if WeekMenu.find(WeekMenu.filename == filename).first_or_none() is not None:
            log.info(f'Menu with checksum {filename} already exists')
            return
        if ((df := extractor.img_to_dataframe(image)) is None) or (p := extractor.period_of_validity(image)) is None:
            log.warning(f'Failed to extract menu from image')
            return
        log.info(f'Extracted dataframe with {df.shape[0]} rows and {df.shape[1]} columns')
        log.info(f'Extracted time period: {utils.timestamp_to_date(p[0])} - {utils.timestamp_to_date(p[1])}')
        postprocess.dataframe_to_week_menu(df, p, filename).insert()
        if self.__settings.ocr_save_images:
            database.fs.put(image, filename=filename)
        log.info(f'Inserted menu with filename {filename}')
