import re
import time

import itzmenu_extractor.ocr.extractor as extractor
from itzmenu_api.persistence.enums import WeekDay


class TestExtractor:

    @staticmethod
    def test_img_to_dataframe_column_correct(week_menu: bytes):
        df = extractor.img_to_dataframe(week_menu)
        assert ([WeekDay.MONDAY, WeekDay.TUESDAY, WeekDay.WEDNESDAY, WeekDay.THURSDAY, WeekDay.FRIDAY]
                == df.columns.tolist())

    @staticmethod
    def test_img_to_dataframe_index_correct(week_menu: bytes):
        df = extractor.img_to_dataframe(week_menu)
        assert df.index.tolist() == ['Suppe', 'Heimatküche', 'From the Bowl', 'Front Cooking', 'Naschglück',
                                     'Naschglück']

    @staticmethod
    def test_img_to_dataframe_prices_at_end(week_menu: bytes):
        df = extractor.img_to_dataframe(week_menu)
        # Check if each cell end with a price
        has_price = df.map(lambda x: re.search(r'\d+.\d+$', x) is not None)
        # Check if all values in each row are True
        all_have_prices = has_price.all(axis=1)
        # Assert that all values are True
        assert all_have_prices.all(), "Not all rows contain a price at the end."

    @staticmethod
    def test_img_to_dataframe_cache_one(week_menu: bytes):
        df = extractor.img_to_dataframe(week_menu)
        start = time.time()
        df2 = extractor.img_to_dataframe(week_menu)
        stop = time.time()
        assert df.equals(df2)
        assert stop - start < 1

    @staticmethod
    def test_img_to_dataframe_cache_multiple(week_menu: bytes, week_menu_holiday: bytes):
        df1 = extractor.img_to_dataframe(week_menu)
        df2 = extractor.img_to_dataframe(week_menu_holiday)
        start = time.time()
        df3 = extractor.img_to_dataframe(week_menu)
        df4 = extractor.img_to_dataframe(week_menu_holiday)
        stop = time.time()
        assert df1.equals(df3)
        assert df2.equals(df4)
        assert not df3.equals(df4)
        assert stop - start < 1

    @staticmethod
    def test_period_of_validity_timestamp(week_menu: bytes):
        period = extractor.period_of_validity(week_menu)
        assert period is not None
        assert period[0] == 1708297200
        assert period[1] == 1708901999

    @staticmethod
    def test_period_of_validity_cache_one(week_menu: bytes):
        period1 = extractor.period_of_validity(week_menu)
        start = time.time()
        period2 = extractor.period_of_validity(week_menu)
        stop = time.time()
        assert period1 == period2
        assert stop - start < 1

    @staticmethod
    def test_period_of_validity_cache_multiple(week_menu: bytes, week_menu_holiday: bytes):
        period1 = extractor.period_of_validity(week_menu)
        period2 = extractor.period_of_validity(week_menu_holiday)
        start = time.time()
        period3 = extractor.period_of_validity(week_menu)
        period4 = extractor.period_of_validity(week_menu_holiday)
        stop = time.time()
        assert period1 == period3
        assert period2 == period4
        assert period3 != period4
        assert stop - start < 1
