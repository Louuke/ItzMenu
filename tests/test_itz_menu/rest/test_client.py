from itz_menu.rest.client import MenuClient


class TestClient:

    def test_menu_client_get_week_menu_success(self, httpserver):
        menu_client = MenuClient('http://127.0.0.1:8080')
        image = menu_client.get_week_menu()
        assert isinstance(image, bytes)
        assert len(image) > 0

    def test_menu_client_get_week_menu_failure(self, httpserver):
        menu_client = MenuClient('http://127.0.0.1:8081')
        image = menu_client.get_week_menu()
        assert image is None
