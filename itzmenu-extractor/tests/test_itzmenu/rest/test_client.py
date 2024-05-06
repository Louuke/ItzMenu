from itzmenu_extractor.rest.client import MenuClient
import itzmenu_extractor.util.image as image


class TestClient:

    def test_menu_client_get_week_menu_success(self, httpserver):
        menu_client = MenuClient('http://127.0.0.1:8080')
        img = menu_client.get_week_menu()
        assert isinstance(img, bytes)
        assert len(img) > 0
        assert image.bytes_to_sha256(img) == 'c0f2190a1b6536ff868fe2436993e25814c763c98db8068ca4c27ce78dfb68a6'

    def test_menu_client_get_week_menu_failure(self, httpserver):
        menu_client = MenuClient('http://127.0.0.1:8081')
        img = menu_client.get_week_menu()
        assert img is None
