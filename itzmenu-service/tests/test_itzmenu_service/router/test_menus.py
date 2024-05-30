import time

import pytest
from httpx import AsyncClient

from itzmenu_service.persistence.adapter.adapter import BeanieWeekMenuDatabase
from itzmenu_service.router.common import ErrorCode


@pytest.mark.asyncio(scope='session')
class TestMenusRouter:
    valid_create_data = {'start_timestamp': 1,
                         'end_timestamp': 5,
                         'created_at': 1,
                         'filename': 'test1.jpg',
                         'menus': [
                             {'name': 'monday',
                              'categories': [{'name': 'test', 'meals': [{'name': 'test', 'price': 1.0}]}]},
                             {'name': 'tuesday',
                              'categories': [{'name': 'test', 'meals': [{'name': 'test', 'price': 2.5}]}]}
                         ]}
    invalid_create_data = {'start_timestamp': 1, 'filename': 'test2.jpg'}
    partial_create_data = {'start_timestamp': 1, 'end_timestamp': 5, 'filename': 'test3.jpg'}

    @pytest.mark.dependency()
    async def test_create_menu(self, http_client: AsyncClient, menu_db: BeanieWeekMenuDatabase):
        response = await http_client.post('/menus', json=self.valid_create_data)
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
        menu = await menu_db.get_by_id(resp['id'])
        assert menu is not None

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu'])
    async def test_create_menu_duplicate(self, http_client: AsyncClient, menu_db: BeanieWeekMenuDatabase):
        count = await menu_db.count()
        response = await http_client.post('/menus', json=self.valid_create_data)
        assert response.status_code == 400
        resp = response.json()
        assert resp['detail'] == ErrorCode.MENU_WITH_FILENAME_ALREADY_EXISTS
        assert count == await menu_db.count()

    async def test_create_menu_partial(self, http_client: AsyncClient):
        response = await http_client.post('/menus', json=self.partial_create_data)
        assert response.status_code == 201
        resp = response.json()
        assert resp['filename'] == self.partial_create_data['filename']
        assert resp['start_timestamp'] == self.partial_create_data['start_timestamp']
        assert resp['end_timestamp'] == self.partial_create_data['end_timestamp']
        assert resp['created_at'] > time.time() - 5
        assert len(resp['menus']) == 0

    async def test_create_menu_fail(self, http_client: AsyncClient):
        response = await http_client.post('/menus', json=self.invalid_create_data)
        assert response.status_code == 422
        resp = response.json()
        assert resp['detail'][0]['type'] == 'missing'
        assert resp['detail'][0]['loc'] == ['body', 'end_timestamp']
