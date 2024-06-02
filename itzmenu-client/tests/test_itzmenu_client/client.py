from pytest_httpserver import HTTPServer

from itzmenu_api.persistence.schemas import WeekMenuCreate
from itzmenu_client.client import ItzMenuClient


def test_create_menu(user: str, password: str, headers: dict[str, str], httpserver: HTTPServer):
    expect = {'start_timestamp': 30, 'end_timestamp': 40, 'created_at': 30, 'filename': 'test_create_menu1.jpg'}
    resp = {'id': '835849f9-52e9-4479-8cc3-63ac96e75325', **expect}
    httpserver.expect_request('/menus', method='POST', json=expect, headers=headers).respond_with_json(resp)
    httpserver.expect_request('/menus', method='POST', json=expect).respond_with_data(status=401)
    client = ItzMenuClient(user, password, f'http://{httpserver.host}:{httpserver.port}')
    menu = WeekMenuCreate(start_timestamp=30, end_timestamp=40, created_at=30, filename='test_create_menu1.jpg')
    response = client.create_menu(menu)
    assert response.id is not None
    assert response.start_timestamp == 30
    assert response.end_timestamp == 40
    assert response.created_at == 30
    assert response.filename == 'test_create_menu1.jpg'
