import numpy as np
import pandas as pd
import pytest

import itzmenu.ocr.extractor as extractor
from itzmenu.persistence.enums import WeekDay


@pytest.fixture(scope='class')
def df(week_menu: bytes) -> pd.DataFrame:
    validity = extractor.period_of_validity(week_menu)
    return extractor.img_to_dataframe(week_menu, validity)


class TestTableExtractor:

    @staticmethod
    def test_as_data_frame_columns_correct(df: pd.DataFrame):
        assert ([WeekDay.MONDAY, WeekDay.TUESDAY, WeekDay.WEDNESDAY, WeekDay.THURSDAY, WeekDay.FRIDAY]
                == df.columns.tolist())

    @staticmethod
    def test_as_data_frame_index_correct(df: pd.DataFrame):
        assert ['Suppe', 'Suppe', 'Heimatküche', 'Heimatküche', 'From the Bowl', 'From the Bowl', 'Front Cooking',
                'Front Cooking', 'Naschglück', 'Naschglück', 'Naschglück', 'Naschglück'] == df.index.tolist()

    @staticmethod
    def test_every_second_row_contains_float(df: pd.DataFrame):
        # Select every second row
        df_second_rows = df.iloc[1::2]
        # Check if each cell contains a float
        is_float = df_second_rows.map(np.isreal)
        # Check if all values in each row are True
        all_floats = is_float.all(axis=1)
        # Assert that all values are True
        assert all_floats.all(), "Not all values in every second row are floats."

    @staticmethod
    def test_every_second_row_contains_description(df: pd.DataFrame):
        # Select every second row
        df_second_rows = df.iloc[::2]
        # Check if each cell contains a string
        is_string = df_second_rows.map(lambda x: isinstance(x, str))
        # Check if all values in each row are True
        all_strings = is_string.all(axis=1)
        # Assert that all values are True
        assert all_strings.all(), "Not all values in every second row are strings."

    @staticmethod
    def test_period_of_validity_timestamp(week_menu: bytes):
        period = extractor.period_of_validity(week_menu)
        assert period is not None
        assert period[0] == 1708297200
        assert period[1] == 1708729199
