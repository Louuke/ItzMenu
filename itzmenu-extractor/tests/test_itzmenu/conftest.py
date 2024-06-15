import hashlib
from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer


@pytest.fixture
def httpserver(make_httpserver):
    server: HTTPServer = make_httpserver
    yield server
    server.clear()


@pytest.fixture
def week_menu() -> bytes:
    return (Path(__file__).parents[1] / 'resources' / 'speiseplanWeek.jpg').read_bytes()


@pytest.fixture
def week_menu_holiday() -> bytes:
    return (Path(__file__).parents[1] / 'resources' / 'speiseplanWeekHoliday.jpg').read_bytes()


@pytest.fixture
def week_menu_csv_path() -> Path:
    return Path(__file__).parents[1] / 'resources' / 'speiseplanWeek.csv'


@pytest.fixture
def week_menu_checksum(week_menu: bytes) -> str:
    return hashlib.sha256(week_menu).hexdigest()
