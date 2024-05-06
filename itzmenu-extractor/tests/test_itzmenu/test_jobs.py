import io
import time

from PIL import Image
import pytest

import itzmenu_extractor.util.image as image
import itzmenu_extractor.jobs as jobs
from itzmenu_extractor.persistence.models import WeekMenu
from itzmenu_extractor.rest.client import MenuClient


@pytest.fixture
def week_menu(week_menu: bytes, event_loop) -> bytes:
    def delete():
        checksum = image.bytes_to_sha256(week_menu)
        event_loop.run_until_complete(WeekMenu.find_one(WeekMenu.filename == f'{checksum}.jpg').delete())
    delete()
    yield week_menu
    delete()


@pytest.fixture
def http_week_menu(event_loop, httpserver):
    def delete(c: MenuClient):
        week_menu = c.get_week_menu()
        checksum = image.bytes_to_sha256(week_menu)
        event_loop.run_until_complete(WeekMenu.find_one(WeekMenu.filename == f'{checksum}.jpg').delete())
    client = MenuClient()
    delete(client)
    yield
    delete(client)


class TestProcessImage:

    def test_process_image_success(self, week_menu: bytes, event_loop, init_database):
        count_before = event_loop.run_until_complete(WeekMenu.count())
        event_loop.run_until_complete(jobs.process_image(week_menu))
        count_after = event_loop.run_until_complete(WeekMenu.count())
        assert count_after == count_before + 1

    def test_process_image_duplicate(self, week_menu: bytes, event_loop, init_database):
        event_loop.run_until_complete(jobs.process_image(week_menu))
        count_before = event_loop.run_until_complete(WeekMenu.count())
        event_loop.run_until_complete(jobs.process_image(week_menu))
        count_after = event_loop.run_until_complete(WeekMenu.count())
        assert count_after == count_before

    def test_process_image_period_of_validity_none(self, event_loop, init_database):
        img = io.BytesIO()
        Image.new('RGB', (10, 10), 'white').save(img, format='JPEG')
        start = time.time()
        event_loop.run_until_complete(jobs.process_image(img.getvalue()))
        end = time.time()
        assert end - start < 1


class TestFetchMenu:

    def test_fetch_menu_success(self, event_loop, http_week_menu, init_database):
        count_before = event_loop.run_until_complete(WeekMenu.count())
        event_loop.run_until_complete(jobs.fetch_menu())
        count_after = event_loop.run_until_complete(WeekMenu.count())
        assert count_after == count_before + 1

    def test_fetch_menu_duplicate(self, event_loop, http_week_menu, init_database):
        event_loop.run_until_complete(jobs.fetch_menu())
        count_before = event_loop.run_until_complete(WeekMenu.count())
        event_loop.run_until_complete(jobs.fetch_menu())
        count_after = event_loop.run_until_complete(WeekMenu.count())
        assert count_after == count_before

    def test_fetch_menu_period_of_validity_none(self, event_loop, init_database):
        img = io.BytesIO()
        Image.new('RGB', (10, 10), 'white').save(img, format='JPEG')
        start = time.time()
        event_loop.run_until_complete(jobs.fetch_menu())
        end = time.time()
        assert end - start < 1
