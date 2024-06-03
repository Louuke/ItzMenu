import time

import pytest
from httpx import AsyncClient

from itzmenu_service.persistence.models import WeekMenu
from itzmenu_service.router.common import ErrorCode


@pytest.mark.asyncio(scope='session')
class TestMenusRouter:
    valid_create_data = {'start_timestamp': 1,
                         'end_timestamp': 5,
                         'created_at': 1,
                         'filename': 'router_menus_test1.jpg',
                         'menus': [
                             {'name': 'monday',
                              'categories': [{'name': 'test', 'meals': [{'name': 'test', 'price': 1.0}]}]},
                             {'name': 'tuesday',
                              'categories': [{'name': 'test', 'meals': [{'name': 'test', 'price': 2.5}]}]}
                         ]}
    superuser_create_data = {'start_timestamp': 20, 'end_timestamp': 25, 'filename': 'router_menus_test9.jpg'}
    invalid_create_data = {'start_timestamp': 1, 'filename': 'router_menus_test2.jpg'}
    partial_create_data = {'start_timestamp': 6, 'end_timestamp': 10, 'filename': 'router_menus_test3.jpg'}
    valid_change_data = {'filename': 'router_menus_test5.jpg', 'start_timestamp': 11, 'end_timestamp': 20}
    superuser_change_data = {'start_timestamp': 21}
    invalid_change_data_id = {'id': '95eae770-42f9-4828-878e-23a28bb06439'}
    invalid_change_data_filename = {'filename': valid_change_data['filename']}

    @pytest.mark.dependency()
    async def test_create_menu(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str]):
        await WeekMenu.find().delete()
        response = await http_client.post('/menus', json=self.valid_create_data, headers=user_w_permissions_headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp['filename'] == self.valid_create_data['filename']
        assert resp['start_timestamp'] == self.valid_create_data['start_timestamp']
        assert resp['end_timestamp'] == self.valid_create_data['end_timestamp']
        assert len(resp['menus']) == 2
        assert resp['menus'][0]['name'] == 'monday'
        assert len(resp['menus'][0]['categories']) == 1
        assert resp['menus'][0]['categories'][0]['name'] == 'test'
        assert len(resp['menus'][0]['categories'][0]['meals']) == 1
        menu = await WeekMenu.get(resp['id'])
        assert menu is not None

    async def test_create_menu_no_headers(self, http_client: AsyncClient):
        response = await http_client.post('/menus', json=self.valid_create_data)
        assert response.status_code == 401

    async def test_create_menu_no_permissions(self, http_client: AsyncClient,
                                              user_wo_permissions_headers: dict[str, str]):
        response = await http_client.post('/menus', json=self.valid_create_data,
                                          headers=user_wo_permissions_headers)
        assert response.status_code == 403

    async def test_create_menu_superuser(self, http_client: AsyncClient, user_superuser_headers: dict[str, str]):
        response = await http_client.post('/menus', json=self.superuser_create_data, headers=user_superuser_headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp['filename'] == self.superuser_create_data['filename']
        assert resp['start_timestamp'] == self.superuser_create_data['start_timestamp']
        assert resp['end_timestamp'] == self.superuser_create_data['end_timestamp']
        assert len(resp['menus']) == 0

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu'])
    async def test_create_menu_duplicate(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str]):
        count = await WeekMenu.count()
        response = await http_client.post('/menus', json=self.valid_create_data, headers=user_w_permissions_headers)
        assert response.status_code == 400
        resp = response.json()
        assert resp['detail'] == ErrorCode.MENU_WITH_FILENAME_ALREADY_EXISTS
        assert count == await WeekMenu.count()

    @pytest.mark.dependency()
    async def test_create_menu_partial(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str]):
        response = await http_client.post('/menus', json=self.partial_create_data,
                                          headers=user_w_permissions_headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp['filename'] == self.partial_create_data['filename']
        assert resp['start_timestamp'] == self.partial_create_data['start_timestamp']
        assert resp['end_timestamp'] == self.partial_create_data['end_timestamp']
        assert resp['created_at'] > time.time() - 5
        assert len(resp['menus']) == 0

    async def test_create_menu_fail(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str]):
        response = await http_client.post('/menus', json=self.invalid_create_data,
                                          headers=user_w_permissions_headers)
        assert response.status_code == 422
        resp = response.json()
        assert resp['detail'][0]['type'] == 'missing'
        assert resp['detail'][0]['loc'] == ['body', 'end_timestamp']

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu'])
    async def test_get_menu_by_id(self, http_client: AsyncClient):
        menu = await WeekMenu.find_one({'filename': self.valid_create_data['filename']})
        response = await http_client.get(f'/menus/menu/{menu.id}')
        assert response.status_code == 200
        resp = response.json()
        assert str(menu.id) == resp['id']
        assert resp['filename'] == self.valid_create_data['filename']
        assert resp['start_timestamp'] == self.valid_create_data['start_timestamp']
        assert resp['end_timestamp'] == self.valid_create_data['end_timestamp']
        assert len(resp['menus']) == 2

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp_range_all(self, http_client: AsyncClient):
        response = await http_client.get('/menus')
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) >= 2
        assert resp[0]['filename'] == self.valid_create_data['filename']
        assert resp[1]['filename'] == self.partial_create_data['filename']

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp_range_end(self, http_client: AsyncClient):
        response = await http_client.get('/menus?end=5')
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 1
        assert resp[0]['filename'] == self.valid_create_data['filename']

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp_range_start(self, http_client: AsyncClient):
        response = await http_client.get('/menus?start=3')
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == await WeekMenu.count() - 1
        assert resp[0]['filename'] == self.partial_create_data['filename']

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp_range_start_and_stop(self, http_client: AsyncClient):
        response = await http_client.get('/menus?start=3&end=15')
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 1
        assert resp[0]['filename'] == self.partial_create_data['filename']

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp_range_no_results(self, http_client: AsyncClient):
        response = await http_client.get('/menus?start=100')
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 0

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp(self, http_client: AsyncClient):
        response = await http_client.get('/menus/menu?timestamp=1')
        assert response.status_code == 200
        resp = response.json()
        assert isinstance(resp, dict)
        assert resp['filename'] == self.valid_create_data['filename']
        response = await http_client.get('/menus/menu?timestamp=7')
        assert response.status_code == 200
        resp = response.json()
        assert isinstance(resp, dict)
        assert resp['filename'] == self.partial_create_data['filename']

    @pytest.mark.dependency()
    async def test_update_menu(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str]):
        menu = WeekMenu(filename='router_menus_test4.jpg', start_timestamp=11, end_timestamp=20, created_at=11)
        resp = await menu.create()
        assert resp.id is not None
        response = await http_client.patch(f'/menus/menu/{resp.id}', json=self.valid_change_data,
                                           headers=user_w_permissions_headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp['filename'] == self.valid_change_data['filename']
        assert resp['start_timestamp'] == self.valid_change_data['start_timestamp']
        assert resp['end_timestamp'] == self.valid_change_data['end_timestamp']

    async def test_update_menu_no_permissions(self, http_client: AsyncClient,
                                              user_wo_permissions_headers: dict[str, str]):
        menu = WeekMenu(filename='router_menus_test10.jpg', start_timestamp=11, end_timestamp=20, created_at=11)
        resp = await menu.create()
        assert resp.id is not None
        response = await http_client.patch(f'/menus/menu/{resp.id}', json=self.valid_change_data,
                                           headers=user_wo_permissions_headers)
        assert response.status_code == 403
        menu = await WeekMenu.get(resp.id)
        assert menu.filename == 'router_menus_test10.jpg'

    async def test_update_menu_superuser(self, http_client: AsyncClient, user_superuser_headers: dict[str, str]):
        menu = WeekMenu(filename='router_menus_test11.jpg', start_timestamp=11, end_timestamp=20, created_at=11)
        resp = await menu.create()
        assert resp.id is not None
        response = await http_client.patch(f'/menus/menu/{resp.id}', json=self.superuser_change_data,
                                           headers=user_superuser_headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp['filename'] == menu.filename
        assert resp['start_timestamp'] == self.superuser_change_data['start_timestamp']
        assert resp['end_timestamp'] == menu.end_timestamp

    async def test_update_menu_id_fail(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str]):
        menu = WeekMenu(filename='router_menus_test6.jpg', start_timestamp=11, end_timestamp=20, created_at=11)
        dao = await menu.create()
        assert dao.id is not None
        response = await http_client.patch(f'/menus/menu/{dao.id}', json=self.invalid_change_data_id,
                                           headers=user_w_permissions_headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp['id'] != self.invalid_change_data_id['id']
        assert resp['id'] == str(dao.id)
        assert resp['filename'] == 'router_menus_test6.jpg'

    @pytest.mark.dependency(depends=['TestMenusRouter::test_update_menu'])
    async def test_update_menu_filename_fail(self, http_client: AsyncClient,
                                             user_w_permissions_headers: dict[str, str]):
        menu = WeekMenu(filename='router_menus_test7.jpg', start_timestamp=11, end_timestamp=20, created_at=11)
        dao = await menu.create()
        assert dao.id is not None
        response = await http_client.patch(f'/menus/menu/{dao.id}', json=self.invalid_change_data_filename,
                                           headers=user_w_permissions_headers)
        assert response.status_code == 400
        resp = response.json()
        assert resp['detail'] == ErrorCode.MENU_WITH_FILENAME_ALREADY_EXISTS
        dao = await WeekMenu.get(dao.id)
        assert dao.filename == menu.filename

    async def test_delete_menu(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str]):
        menu = WeekMenu(filename='router_menus_test8.jpg', start_timestamp=11, end_timestamp=20, created_at=11)
        dao = await menu.create()
        assert dao.id is not None
        response = await http_client.delete(f'/menus/menu/{dao.id}', headers=user_w_permissions_headers)
        assert response.status_code == 204
        assert await WeekMenu.get(dao.id) is None
        response = await http_client.delete(f'/menus/menu/{dao.id}', headers=user_w_permissions_headers)
        assert response.status_code == 404
        assert await WeekMenu.get(dao.id) is None

    async def test_delete_menu_no_permissions(self, http_client: AsyncClient,
                                              user_wo_permissions_headers: dict[str, str]):
        menu = WeekMenu(filename='router_menus_test12.jpg', start_timestamp=11, end_timestamp=20, created_at=11)
        dao = await menu.create()
        assert dao.id is not None
        response = await http_client.delete(f'/menus/menu/{dao.id}', headers=user_wo_permissions_headers)
        assert response.status_code == 403
        assert await WeekMenu.get(dao.id) is not None

    async def test_delete_menu_superuser(self, http_client: AsyncClient, user_superuser_headers: dict[str, str]):
        menu = WeekMenu(filename='router_menus_test13.jpg', start_timestamp=11, end_timestamp=20, created_at=11)
        dao = await menu.create()
        assert dao.id is not None
        response = await http_client.delete(f'/menus/menu/{dao.id}', headers=user_superuser_headers)
        assert response.status_code == 204
        assert await WeekMenu.get(dao.id) is None
        response = await http_client.delete(f'/menus/menu/{dao.id}', headers=user_superuser_headers)
        assert response.status_code == 404
        assert await WeekMenu.get(dao.id) is None
