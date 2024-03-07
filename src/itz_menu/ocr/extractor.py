import io
import re
import time
import pytesseract
import PIL.Image as PImage
import pandas as pd

from datetime import datetime
from img2table.document import Image
from img2table.ocr import TesseractOCR
from img2table.tables.objects.extraction import ExtractedTable

import itz_menu.ocr.preprocessing as preprocessing
from itz_menu.persistence.enums import WeekDay


class TableExtractor:

    def __init__(self, threads=1, lang='deu'):
        self.__ocr = TesseractOCR(n_threads=threads, lang=lang)

    def as_data_frame(self, image: bytes) -> pd.DataFrame | None:
        if (preprocessed := preprocessing.threshold(image)) is not None:
            img = Image(src=preprocessed)
            if len(tables := img.extract_tables(ocr=self.__ocr, borderless_tables=True, min_confidence=30)) > 0:
                return self.__post_process(tables)

    @staticmethod
    def timestamps(image: bytes) -> tuple[int, int] | None:
        buffer = io.BytesIO(image)
        if type(result := pytesseract.image_to_string(PImage.open(buffer), lang='deu')) is str:
            if (match := re.search(r'\d\d.\d\d.\d\d\d\d', result)) is not None:
                end_date = datetime.strptime(match.group(), '%d.%m.%Y')
                end_timestamp = int(time.mktime(end_date.timetuple())) + 86399
                start_timestamp = end_timestamp - 431999
                return start_timestamp, end_timestamp

    def __post_process(self, tables: list[ExtractedTable]) -> pd.DataFrame:
        # Concatenate all tables
        df = pd.concat([table.df for table in tables], ignore_index=True)
        # Transform rows
        df = self.__transform_rows(df)
        # Set column names
        self.__set_column_names(df)
        # Fill row names
        self.__fill_row_names(df)
        df = df.bfill(axis=1)
        df = df.iloc[:, :6]
        return df.set_index(df.columns[0])

    @staticmethod
    def __set_column_names(df: pd.DataFrame):
        """ Set the first row as column names and drop it """
        df.columns = df.iloc[0].map(lambda x: WeekDay.find_by_value(x), na_action='ignore')
        df.drop(index=0, inplace=True, errors='ignore')

    def __transform_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """ Replace newlines with spaces and reformat price format """
        df.replace('\n', ' ', regex=True, inplace=True)
        return df.applymap(self.__update_prices, na_action='ignore')

    @staticmethod
    def __update_prices(cell: str) -> float | str:
        """ Replace comma with dot and remove euro sign """
        if re.match(r'^\d+(,|.)\d+\s?€$', cell):
            return float(cell.replace(',', '.').replace('€', '').strip())
        return cell

    @staticmethod
    def __fill_row_names(df: pd.DataFrame):
        for i in range(0, len(df), 2):
            first = df.iloc[i, 0]
            second = df.iloc[i + 1, 0]
            value = first if first else second
            df.iloc[i, 0] = value
            df.iloc[i + 1, 0] = value
