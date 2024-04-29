import io
import re
import time
from datetime import datetime

import PIL.Image as PImage
import pandas as pd
import pytesseract
from img2table.document import Image
from img2table.ocr.base import OCRInstance
from img2table.ocr import TesseractOCR, VisionOCR
from img2table.tables.objects.extraction import ExtractedTable

import itzmenu.utils as utils
import itzmenu.ocr.preprocess as preprocess
from itzmenu.config.settings import Settings
from itzmenu.persistence.enums import WeekDay


@preprocess.crop_main_image_content
def img_to_dataframe(image: bytes, validity_period: tuple[int, int]) -> pd.DataFrame | None:
    image = preprocess.hide_holidays(image, validity_period)
    return __img_to_dataframe(image)


@preprocess.apply_threshold
def __img_to_dataframe(image: bytes) -> pd.DataFrame | None:
    ocr = __create_ocr_instance()
    img = Image(src=image)
    if len(tables := img.extract_tables(ocr=ocr, min_confidence=30)) > 0:
        return __post_process(tables)


def __create_ocr_instance() -> OCRInstance:
    if (settings := Settings()).google_cloud_vision_enabled and not utils.is_test_running():
        return VisionOCR(api_key=settings.google_cloud_vision_api_key)
    return TesseractOCR(n_threads=1, lang='deu')


@preprocess.apply_threshold
def period_of_validity(image: bytes, lang: str = 'deu') -> tuple[int, int] | None:
    buffer = io.BytesIO(image)
    if type(result := pytesseract.image_to_string(PImage.open(buffer), lang=lang)) is str:
        if (match := re.search(r'- \d\d.\d\d.\d\d\d\d', result)) is not None:
            end_date = datetime.strptime(match.group().replace('- ', ''), '%d.%m.%Y')
            end_timestamp = int(time.mktime(end_date.timetuple())) + 86399
            start_timestamp = end_timestamp - 431999
            return start_timestamp, end_timestamp


def __post_process(tables: list[ExtractedTable]) -> pd.DataFrame:
    # Concatenate all tables
    df = pd.concat([table.df for table in tables], ignore_index=True)
    # Drop empty rows
    df.dropna(subset=df.columns[1:], how='all', inplace=True)
    # Transform rows
    df = __transform_rows(df)
    # Set column names
    __set_column_names(df)
    # Fill row names
    __fill_row_names(df)
    df = df.bfill(axis=1)
    df = df.iloc[:, :6]
    return df.set_index(df.columns[0])


def __set_column_names(df: pd.DataFrame):
    """ Set the first row as column names and drop it """
    df.columns = df.iloc[0].map(lambda x: WeekDay.find_by_value(x), na_action='ignore')
    df.drop(index=0, inplace=True, errors='ignore')


def __transform_rows(df: pd.DataFrame) -> pd.DataFrame:
    """ Replace newlines with spaces and reformat price format """
    df.replace('\n', ' ', regex=True, inplace=True)
    df = df.map(__update_prices, na_action='ignore')
    # Replace ( x ) with (x)
    df.replace(r'\(\s(.*?)\s\)', r'(\1)', regex=True, inplace=True)
    return df


def __update_prices(cell: str) -> float | str:
    """ Replace comma with dot and remove euro sign """
    if re.match(r'^\d+(,|.)\d+\s?.$', cell):
        return float(cell.replace(',', '.')[:-1].strip())
    return cell


def __fill_row_names(df: pd.DataFrame):
    for i in range(0, len(df), 2):
        first = df.iloc[i, 0]
        second = df.iloc[i + 1, 0]
        value = first if first else second
        df.iloc[i, 0] = value
        df.iloc[i + 1, 0] = value
