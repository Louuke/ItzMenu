import re

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
        assert df.index.tolist() == ['Suppe', 'Heimatküche', 'From the Bowl', 'Front Cooking', 'Naschglück',
                                     'Naschglück']

    @staticmethod
    def test_every_row_contains_price_at_end(df: pd.DataFrame):
        # Check if each cell end with a price
        has_price = df.map(lambda x: re.search(r'\d+.\d+$', x) is not None)
        # Check if all values in each row are True
        all_have_prices = has_price.all(axis=1)
        # Assert that all values are True
        assert all_have_prices.all(), "Not all rows contain a price at the end."

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
