from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer


@pytest.fixture()
def httpserver(make_httpserver, week_menu: bytes):
    server: HTTPServer = make_httpserver
    server.expect_request('/media/img/speiseplanWeek.jpg', method='GET').respond_with_data(week_menu)
    yield server
    server.clear()


@pytest.fixture(scope='session')
def week_menu() -> bytes:
    return (Path(__file__).parents[1] / 'resources' / 'speiseplanWeek.jpg').read_bytes()


@pytest.fixture(scope='session')
def week_menu_holiday() -> bytes:
    return (Path(__file__).parents[1] / 'resources' / 'speiseplanWeekHoliday.jpg').read_bytes()
