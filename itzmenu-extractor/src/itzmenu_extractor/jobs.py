import logging as log
import re
from argparse import Namespace
from datetime import datetime

from apscheduler.schedulers.blocking import BlockingScheduler

import itzmenu_extractor.ocr.extractor as extractor
import itzmenu_extractor.ocr.postprocess as postprocess
import itzmenu_extractor.util.image as image
import itzmenu_extractor.util.time as time
from itzmenu_extractor.rest.client import MenuClient
from itzmenu_extractor.config.settings import Settings
from itzmenu_client.client import ItzMenuClient


class Executor:
    def __init__(self, args: Namespace):
        log.basicConfig(level=args.log.upper())
        self.__settings = s = Settings()
        self.__scheduler = BlockingScheduler()
        self.__menu_client = MenuClient()
        self.__itz_client = ItzMenuClient(s.itz_menu_user_email, s.itz_menu_user_password, s.itz_menu_host)
        self.__args = args
        self.__scheduler.add_job(self.fetch_menu, 'interval', seconds=s.ocr_check_interval,
                                 next_run_time=datetime.now())
        self.__scheduler.add_job(self.preload_menu)

    def start(self):
        return self.__scheduler.start()

    def stop(self):
        return self.__scheduler.shutdown()

    def preload_menu(self):
        for value in self.__args.preload:
            if re.match(r'^([A-Z]:)?[a-zA-Z0-9\\/_-]+\.jpg$', value) is not None:
                self.process_image(image.load_image(value))
            else:
                log.warning(f'Invalid filename: {value}')

    def fetch_menu(self):
        if (menu := self.__menu_client.get_week_menu()) is None:
            return
        log.info(f'Received menu with {len(menu)} bytes')
        self.process_image(menu)

    def process_image(self, img: bytes):
        checksum = f'{image.bytes_to_sha256(img)}'
        if self.__itz_client.get_menu_by_id_or_checksum(checksum) is not None:
            log.info(f'Menu with checksum {checksum} already exists')
            return
        if (p := extractor.period_of_validity(img)) is None or (df := extractor.img_to_dataframe(img)) is None:
            log.warning(f'Failed to extract menu from image')
            return
        log.info(f'Extracted dataframe with {df.shape[0]} rows and {df.shape[1]} columns')
        log.info(f'Extracted time period: {time.timestamp_to_date(p[0])} - {time.timestamp_to_date(p[1])}')
        img_base64 = image.bytes_to_base64(img) if self.__settings.ocr_save_images else None
        menu = postprocess.dataframe_to_week_menu(df, p, checksum, img_base64)
        if (resp := self.__itz_client.create_menu(menu)) is not None:
            log.info(f'Inserted menu with id {resp.id}')
        else:
            log.warning(f'Failed to insert menu')
