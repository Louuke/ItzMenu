import time

import random as rand
from datetime import date

import pytest

from itz_menu.time import is_holiday


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
def day_of_work_timestamp(year: int) -> int:
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
    def test_day_of_work_is_holiday(year: int):
        assert is_holiday(date(year, 5, 1))

    @staticmethod
    def test_day_of_work_is_holiday_timestamp(day_of_work_timestamp: int):
        assert is_holiday(day_of_work_timestamp)
