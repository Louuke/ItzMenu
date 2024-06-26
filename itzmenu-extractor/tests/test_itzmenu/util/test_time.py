import time

import random as rand
from datetime import date

import pytest

from itzmenu_extractor.util.time import is_holiday, timestamp_to_date


@pytest.fixture
def year() -> int:
    return rand.randint(1970, 2100)


@pytest.fixture
def christmas_timestamp(year: int) -> int:
    d = date(year, 12, 24)
    return int(time.mktime(d.timetuple()))


@pytest.fixture
def new_year_timestamp(year: int) -> int:
    d = date(year, 12, 31)
    return int(time.mktime(d.timetuple()))


@pytest.fixture
def labour_day_timestamp(year: int) -> int:
    d = date(year, 5, 1)
    return int(time.mktime(d.timetuple()))


class TestCompanyHolidays:

    @staticmethod
    def test_christmas_eve_is_holiday(year: int):
        assert is_holiday(date(year, 12, 24))

    @staticmethod
    def test_christmas_eve_is_holiday_timestamp(christmas_timestamp: int):
        assert is_holiday(christmas_timestamp)

    @staticmethod
    def test_new_years_eve_is_holiday(year: int):
        assert is_holiday(date(2024, 12, 31))

    @staticmethod
    def test_new_years_eve_is_holiday_timestamp(new_year_timestamp: int):
        assert is_holiday(new_year_timestamp)

    @staticmethod
    def test_labour_day_is_holiday(year: int):
        assert is_holiday(date(year, 5, 1))

    @staticmethod
    def test_labour_day_is_holiday_timestamp(labour_day_timestamp: int):
        assert is_holiday(labour_day_timestamp)


class TestTimestampToDate:

    def test_timestamp_to_date(self):
        d = timestamp_to_date(1710691628)
        assert d == '17.03.2024'
