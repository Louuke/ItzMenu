from typing import Any
from uuid import UUID

from pytest_httpserver import HTTPServer

from itzmenu_api.persistence.schemas import WeekMenuCreate, WeekMenuUpdate
from itzmenu_client.client import ItzMenuClient


class TestItzMenuClient:

    def test_create_menu(self, user: str, password: str, headers: dict[str, str], httpserver: HTTPServer):
        expect = {'start_timestamp': 30, 'end_timestamp': 40, 'created_at': 30,
                  'img_checksum': 'e0e2eeb7e31c4c4b662a120e59f1df526daf09fca82cb617368e02ea53d162a6'}
        resp = {'id': '835849f9-52e9-4479-8cc3-63ac96e75325', **expect}
        httpserver.expect_request('/menus', method='POST', json=expect, headers=headers).respond_with_json(resp)
        httpserver.expect_request('/menus', method='POST', json=expect).respond_with_data(status=401)
        client = ItzMenuClient(user, password, f'http://{httpserver.host}:{httpserver.port}')
        menu = WeekMenuCreate(start_timestamp=30, end_timestamp=40, created_at=30,
                              img_checksum='e0e2eeb7e31c4c4b662a120e59f1df526daf09fca82cb617368e02ea53d162a6')
        response = client.create_menu(menu)
        assert response.id is not None
        assert response.start_timestamp == 30
        assert response.end_timestamp == 40
        assert response.created_at == 30
        assert response.img_checksum == 'e0e2eeb7e31c4c4b662a120e59f1df526daf09fca82cb617368e02ea53d162a6'

    def test_get_menu_by_id(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        resp = week_menus[0]
        (httpserver.expect_request(f'/menus/menu/{resp["id"]}', method='GET').respond_with_json(resp))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        response = client.get_menu_by_id_or_checksum('835849f9-52e9-4479-8cc3-63ac96e75325')
        assert response.start_timestamp == resp['start_timestamp']
        assert response.end_timestamp == resp['end_timestamp']
        assert response.created_at == resp['created_at']
        assert response.img_checksum == resp['img_checksum']
        assert response.id == UUID(resp['id'])
        assert response.menus == []

    def test_get_menu_by_id_not_found(self, httpserver: HTTPServer):
        (httpserver.expect_request('/menus/menu/835849f9-52e9-4479-8cc3-63ac96e75325', method='GET')
         .respond_with_data(status=404))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        assert client.get_menu_by_id_or_checksum('835849f9-52e9-4479-8cc3-63ac96e75325') is None

    def test_get_menu_by_checksum(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        resp = week_menus[0]
        (httpserver.expect_request(f'/menus/menu/{resp["img_checksum"]}', method='GET').respond_with_json(resp))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        response = client.get_menu_by_id_or_checksum(week_menus[0]['img_checksum'])
        assert response.start_timestamp == resp['start_timestamp']
        assert response.end_timestamp == resp['end_timestamp']
        assert response.created_at == resp['created_at']
        assert response.img_checksum == resp['img_checksum']
        assert response.id == UUID(resp['id'])
        assert response.menus == []

    def test_get_menu_by_timestamp(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        resp1 = week_menus[0]
        (httpserver.expect_request('/menus/menu', method='GET',
                                   query_string=f'timestamp={resp1["start_timestamp"] + 1}')
         .respond_with_json(resp1))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        response = client.get_menu_by_timestamp(resp1['start_timestamp'] + 1)
        assert response.start_timestamp == resp1['start_timestamp']
        assert response.end_timestamp == resp1['end_timestamp']
        assert response.created_at == resp1['created_at']
        assert response.img_checksum == resp1['img_checksum']
        assert response.id == UUID(resp1['id'])
        assert response.menus == []
        resp2 = week_menus[1]
        (httpserver.expect_request('/menus/menu', method='GET', query_string=f'timestamp={resp2["end_timestamp"]}')
         .respond_with_json(resp2))
        response = client.get_menu_by_timestamp(resp2['end_timestamp'])
        assert response.start_timestamp == resp2['start_timestamp']
        assert response.end_timestamp == resp2['end_timestamp']
        assert response.created_at == resp2['created_at']
        assert response.img_checksum == resp2['img_checksum']
        assert response.id == UUID(resp2['id'])
        assert response.menus == []

    def test_get_menu_by_timestamp_range_all(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        httpserver.expect_request('/menus', method='GET').respond_with_json(week_menus)
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        response = client.get_menu_by_timestamp_range()
        assert len(response) == 2
        for i, resp in enumerate(week_menus):
            assert response[i].start_timestamp == resp['start_timestamp']
            assert response[i].end_timestamp == resp['end_timestamp']
            assert response[i].created_at == resp['created_at']
            assert response[i].img_checksum == resp['img_checksum']
            assert response[i].id == UUID(resp['id'])
            assert response[i].menus == []

    def test_get_menu_by_timestamp_end(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        resp = week_menus[1]
        (httpserver.expect_request('/menus', method='GET', query_string=f'start=0&end={resp["end_timestamp"]}')
         .respond_with_json([resp]))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        response = client.get_menu_by_timestamp_range(end=resp['end_timestamp'])
        assert len(response) == 1
        assert response[0].start_timestamp == resp['start_timestamp']
        assert response[0].end_timestamp == resp['end_timestamp']
        assert response[0].created_at == resp['created_at']
        assert response[0].img_checksum == resp['img_checksum']
        assert response[0].id == UUID(resp['id'])
        assert response[0].menus == []

    def test_get_menu_by_timestamp_start(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        resp = week_menus[0]
        (httpserver.expect_request('/menus', method='GET',
                                   query_string=f'start={resp["start_timestamp"] - 2}&end=9999999999')
         .respond_with_json([resp]))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        response = client.get_menu_by_timestamp_range(start=resp['start_timestamp'] - 2)
        assert len(response) == 1
        assert response[0].start_timestamp == resp['start_timestamp']
        assert response[0].end_timestamp == resp['end_timestamp']
        assert response[0].created_at == resp['created_at']
        assert response[0].img_checksum == resp['img_checksum']
        assert response[0].id == UUID(resp['id'])
        assert response[0].menus == []

    def test_get_menu_by_timestamp_start_and_stop(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        (httpserver.expect_request('/menus', method='GET', query_string=f'start={week_menus[0]["start_timestamp"]}'
                                                                        f'&end={week_menus[1]["end_timestamp"]}')
         .respond_with_json(week_menus))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        response = client.get_menu_by_timestamp_range(start=week_menus[0]['start_timestamp'],
                                                      end=week_menus[1]['end_timestamp'])
        assert len(response) == 2
        for i, resp in enumerate(week_menus):
            assert response[i].start_timestamp == resp['start_timestamp']
            assert response[i].end_timestamp == resp['end_timestamp']
            assert response[i].created_at == resp['created_at']
            assert response[i].img_checksum == resp['img_checksum']
            assert response[i].id == UUID(resp['id'])
            assert response[i].menus == []

    def test_get_menu_by_timestamp_no_results(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        (httpserver.expect_request('/menus', method='GET', query_string='start=100&end=9999999999')
         .respond_with_json([]))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        response = client.get_menu_by_timestamp_range(start=100)
        assert response == []

    def test_update_menu(self, httpserver: HTTPServer, user: str, password: str, headers: dict[str, str],
                         week_menus: list[dict[str, Any]]):
        update = {'start_timestamp': 99, 'end_timestamp': 100, 'created_at': 99,
                  'img_checksum': '03043c5abd66e979d1ab97f3be8a1bc2d8ba993b3374c774f93b698e1c8376b7'}
        resp = {'id': '835849f9-52e9-4479-8cc3-63ac96e75325', **update}
        httpserver.expect_request(f'/menus/menu/835849f9-52e9-4479-8cc3-63ac96e75325', method='PATCH', json=update,
                                  headers=headers).respond_with_json(resp)
        (httpserver.expect_request(f'/menus/menu/835849f9-52e9-4479-8cc3-63ac96e75325', method='PATCH', json=update)
         .respond_with_data(status=401))
        client = ItzMenuClient(user, password, f'http://{httpserver.host}:{httpserver.port}')
        response = client.update_menu('835849f9-52e9-4479-8cc3-63ac96e75325',
                                      WeekMenuUpdate(**update))
        assert response.start_timestamp == 99
        assert response.end_timestamp == 100
        assert response.created_at == 99
        assert response.img_checksum == '03043c5abd66e979d1ab97f3be8a1bc2d8ba993b3374c774f93b698e1c8376b7'
        assert response.id == UUID('835849f9-52e9-4479-8cc3-63ac96e75325')

    def test_update_menu_no_permissions(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        update = {'start_timestamp': 99, 'end_timestamp': 100, 'created_at': 99,
                  'img_checksum': week_menus[0]['img_checksum']}
        (httpserver.expect_request(f'/menus/menu/835849f9-52e9-4479-8cc3-63ac96e75325', method='PATCH', json=update)
         .respond_with_data(status=403))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        resp = client.update_menu('835849f9-52e9-4479-8cc3-63ac96e75325', WeekMenuUpdate(**update))
        assert resp is None

    def test_update_menu_filename_fail(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        update = {'start_timestamp': 99, 'end_timestamp': 100, 'created_at': 99,
                  'img_checksum': week_menus[0]['img_checksum']}
        (httpserver.expect_request(f'/menus/menu/835849f9-52e9-4479-8cc3-63ac96e75325', method='PATCH', json=update)
         .respond_with_data(status=400))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        resp = client.update_menu('835849f9-52e9-4479-8cc3-63ac96e75325', WeekMenuUpdate(**update))
        assert resp is None

    def test_delete_menu(self, httpserver: HTTPServer, user: str, password: str, headers: dict[str, str],
                         week_menus: list[dict[str, Any]]):
        (httpserver.expect_request(f'/menus/menu/835849f9-52e9-4479-8cc3-63ac96e75325', method='DELETE',
                                   headers=headers).respond_with_data(status=204))
        (httpserver.expect_request(f'/menus/menu/835849f9-52e9-4479-8cc3-63ac96e75325', method='DELETE')
         .respond_with_data(status=401))
        client = ItzMenuClient(user, password, f'http://{httpserver.host}:{httpserver.port}')
        assert client.delete_menu('835849f9-52e9-4479-8cc3-63ac96e75325')

    def test_delete_menu_no_permissions(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        (httpserver.expect_request(f'/menus/menu/835849f9-52e9-4479-8cc3-63ac96e75325', method='DELETE')
         .respond_with_data(status=403))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        assert not client.delete_menu('835849f9-52e9-4479-8cc3-63ac96e75325')

    def test_delete_menu_not_found(self, httpserver: HTTPServer, week_menus: list[dict[str, Any]]):
        (httpserver.expect_request(f'/menus/menu/835849f9-52e9-4479-8cc3-63ac96e75325', method='DELETE')
         .respond_with_data(status=404))
        client = ItzMenuClient('user', 'password', f'http://{httpserver.host}:{httpserver.port}')
        assert not client.delete_menu('835849f9-52e9-4479-8cc3-63ac96e75325')
