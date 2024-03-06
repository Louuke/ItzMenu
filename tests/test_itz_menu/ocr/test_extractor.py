import numpy as np

from itz_menu.ocr.extractor import TableExtractor
import pandas as pd
import pytest


@pytest.fixture()
def table_extractor() -> TableExtractor:
    return TableExtractor()


@pytest.fixture(scope='class')
def df(week_menu: bytes, table_extractor: TableExtractor) -> pd.DataFrame:
    return table_extractor.as_data_frame(week_menu)


class TestTableExtractor:

    @staticmethod
    def test_as_data_frame_columns_correct(df: pd.DataFrame):
        assert ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag'] == df.columns.tolist()

    @staticmethod
    def test_as_data_frame_index_correct(df: pd.DataFrame):
        assert ['Suppe', 'Suppe', 'Heimatküche', 'Heimatküche', 'From the Bowl', 'From the Bowl', 'Front Cooking',
                'Front Cooking', 'Naschglück', 'Naschglück', 'Naschglück', 'Naschglück'] == df.index.tolist()

    @staticmethod
    def test_every_second_row_contains_float(df: pd.DataFrame):
        # Select every second row
        df_second_rows = df.iloc[1::2]
        # Check if each cell contains a float
        is_float = df_second_rows.applymap(np.isreal)
        # Check if all values in each row are True
        all_floats = is_float.all(axis=1)
        # Assert that all values are True
        assert all_floats.all(), "Not all values in every second row are floats."

    @staticmethod
    def test_every_second_row_contains_description(df: pd.DataFrame):
        print(df.to_string())
        # Select every second row
        df_second_rows = df.iloc[::2]
        # Check if each cell contains a string
        is_string = df_second_rows.applymap(lambda x: isinstance(x, str))
        # Check if all values in each row are True
        all_strings = is_string.all(axis=1)
        # Assert that all values are True
        assert all_strings.all(), "Not all values in every second row are strings."

    @staticmethod
    def test(week_menu: bytes, table_extractor: TableExtractor):
        table_extractor.menu_timestamp(week_menu)
