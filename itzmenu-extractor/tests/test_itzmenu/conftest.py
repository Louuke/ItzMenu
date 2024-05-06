import asyncio
import importlib.resources as pkg_resources
import pytest

import itzmenu_extractor.persistence.database as database


@pytest.fixture(scope='session')
def httpserver_listen_address():
    return '127.0.0.1', 8080


@pytest.fixture()
def httpserver(make_httpserver, week_menu: bytes):
    server = make_httpserver
    server.expect_request('/media/img/speiseplanWeek.jpg', method='GET').respond_with_data(week_menu)
    yield server
    server.clear()


@pytest.fixture(scope='session')
def week_menu() -> bytes:
    return pkg_resources.files('resources').joinpath('speiseplanWeek.jpg').read_bytes()


@pytest.fixture(scope='session')
def week_menu_holiday() -> bytes:
    return pkg_resources.files('resources').joinpath('speiseplanWeekHoliday.jpg').read_bytes()


@pytest.fixture(scope='session')
def event_loop():
    return asyncio.get_event_loop()


@pytest.fixture(scope='session')
def init_database(event_loop):
    event_loop.run_until_complete(database.init())

