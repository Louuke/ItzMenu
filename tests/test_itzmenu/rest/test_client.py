from itzmenu.rest.client import MenuClient
from itzmenu.utils import bytes_to_sha256


class TestClient:

    def test_menu_client_get_week_menu_success(self, httpserver):
        menu_client = MenuClient('http://127.0.0.1:8080')
        image = menu_client.get_week_menu()
        assert isinstance(image, bytes)
        assert len(image) > 0
        assert bytes_to_sha256(image) == 'c0f2190a1b6536ff868fe2436993e25814c763c98db8068ca4c27ce78dfb68a6'

    def test_menu_client_get_week_menu_failure(self, httpserver):
        menu_client = MenuClient('http://127.0.0.1:8081')
        image = menu_client.get_week_menu()
        assert image is None
