from uuid import UUID

from pytest_httpserver import HTTPServer

from itzmenu_api.persistence.schemas import WeekMenuCreate, WeekMenuRead
from itzmenu_client.client import ItzMenuClient


def test_create_menu(user: str, password: str, headers: dict[str, str], httpserver: HTTPServer):
    expect = {'start_timestamp': 30, 'end_timestamp': 40, 'created_at': 30, 'filename': 'test_menu.jpg'}
    resp = {'id': '835849f9-52e9-4479-8cc3-63ac96e75325', **expect}
    httpserver.expect_request('/menus', method='POST', json=expect, headers=headers).respond_with_json(resp)
    httpserver.expect_request('/menus', method='POST', json=expect).respond_with_data(status=401)
    client = ItzMenuClient(user, password, f'http://{httpserver.host}:{httpserver.port}')
    menu = WeekMenuCreate(start_timestamp=30, end_timestamp=40, created_at=30, filename='test_menu.jpg')
    response = client.create_menu(menu)
    assert response.id is not None
    assert response.start_timestamp == 30
    assert response.end_timestamp == 40
    assert response.created_at == 30
    assert response.filename == 'test_create_menu1.jpg'


def test_get_menu_by_id(httpserver: HTTPServer):
    resp = {'id': '835849f9-52e9-4479-8cc3-63ac96e75325', 'start_timestamp': 30, 'end_timestamp': 40, 'created_at': 30,
            'filename': 'test_menu.jpg'}
    httpserver.expect_request('/menus/835849f9-52e9-4479-8cc3-63ac96e75325', method='GET').respond_with_json(resp)
    client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
    response = client.get_menu_by_id('835849f9-52e9-4479-8cc3-63ac96e75325')
    assert response.start_timestamp == 30
    assert response.end_timestamp == 40
    assert response.created_at == 30
    assert response.filename == 'test_menu.jpg'
    assert response.id == UUID('835849f9-52e9-4479-8cc3-63ac96e75325')
    assert response.menus == []