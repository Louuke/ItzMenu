from pytest_httpserver import HTTPServer

from itzmenu_extractor.rest.client import MenuClient
import itzmenu_extractor.util.image as image


class TestClient:

    def test_menu_client_get_week_menu_success(self, httpserver: HTTPServer, week_menu: bytes, week_menu_checksum: str):
        (httpserver.expect_request('/media/img/speiseplanWeek.jpg', method='GET')
         .respond_with_data(week_menu, mimetype='image/jpeg'))
        menu_client = MenuClient(f'http://{httpserver.host}:{httpserver.port}')
        img = menu_client.get_week_menu()
        assert isinstance(img, bytes)
        assert len(img) > 0
        assert image.bytes_to_sha256(img) == week_menu_checksum

    def test_menu_client_get_week_menu_failure(self, httpserver: HTTPServer):
        menu_client = MenuClient(f'http://{httpserver.host}:{httpserver.port}')
        img = menu_client.get_week_menu()
        assert img is None
