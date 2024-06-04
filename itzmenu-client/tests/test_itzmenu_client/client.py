from typing import Any
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
    assert response.filename == 'test_menu.jpg'


def test_get_menu_by_id(httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
    resp = week_menus[0]
    (httpserver.expect_request(f'/menus/menu/{resp["id"]}', method='GET')
     .respond_with_json(resp))
    client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
    response = client.get_menu_by_id('835849f9-52e9-4479-8cc3-63ac96e75325')
    assert response.start_timestamp == resp['start_timestamp']
    assert response.end_timestamp == resp['end_timestamp']
    assert response.created_at == resp['created_at']
    assert response.filename == resp['filename']
    assert response.id == UUID(resp['id'])
    assert response.menus == []


def test_get_menu_by_timestamp(httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
    resp1 = week_menus[0]
    (httpserver.expect_request('/menus/menu', method='GET', query_string=f'timestamp={resp1["start_timestamp"] + 1}')
     .respond_with_json(resp1))
    client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
    response = client.get_menu_by_timestamp(resp1['start_timestamp'] + 1)
    assert response.start_timestamp == resp1['start_timestamp']
    assert response.end_timestamp == resp1['end_timestamp']
    assert response.created_at == resp1['created_at']
    assert response.filename == resp1['filename']
    assert response.id == UUID(resp1['id'])
    assert response.menus == []
    resp2 = week_menus[1]
    (httpserver.expect_request('/menus/menu', method='GET', query_string=f'timestamp={resp2["end_timestamp"]}')
     .respond_with_json(resp2))
    response = client.get_menu_by_timestamp(resp2['end_timestamp'])
    assert response.start_timestamp == resp2['start_timestamp']
    assert response.end_timestamp == resp2['end_timestamp']
    assert response.created_at == resp2['created_at']
    assert response.filename == resp2['filename']
    assert response.id == UUID(resp2['id'])
    assert response.menus == []
