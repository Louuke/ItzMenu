import base64
import hashlib
import time
from typing import Any

import pytest
from httpx import AsyncClient

from itzmenu_service.persistence.models import WeekMenu
from itzmenu_service.router.common import ErrorCode


@pytest.fixture
def menu_image_base64(menu_image: bytes) -> str:
    return image_to_base64(menu_image)


@pytest.fixture
def menu_image_checksum(menu_image: bytes) -> str:
    return image_to_checksum(menu_image)


def image_to_base64(image: bytes) -> str:
    return base64.b64encode(image).decode('utf-8')


def image_to_checksum(image: bytes) -> str:
    return hashlib.sha256(image).hexdigest()


@pytest.fixture
def valid_create_data(menu_image_base64: str, menu_image_checksum: str) -> dict[str, Any]:
    return {'start_timestamp': 1,
            'end_timestamp': 5,
            'created_at': 1,
            'img_checksum': menu_image_checksum,
            'img': menu_image_base64,
            'menus': [
                {'name': 'monday',
                 'categories': [{'name': 'test', 'meals': [{'name': 'test', 'price': 1.0}]}]},
                {'name': 'tuesday',
                 'categories': [{'name': 'test', 'meals': [{'name': 'test', 'price': 2.5}]}]}
            ]}


@pytest.mark.asyncio(scope='session')
class TestMenusRouter:
    superuser_create_data = {'start_timestamp': 20, 'end_timestamp': 25,
                             'img_checksum': '1db4b223e5bfcb904715e3091ef216f4838767e3a84e38979a73c19f67150d6d'}
    invalid_create_data = {'start_timestamp': 1,
                           'img_checksum': '43ed77500258a02c127fa7383373e7eff7936761f00fe4b6506af39768e5509e'}
    partial_create_data = {'start_timestamp': 6, 'end_timestamp': 10, 'img': 'zjtgdj',
                           'img_checksum': '33c97b52e62d07dda131f789decaba164cc37eb647d4faf44f106d7086dd5ad5'}
    valid_change_data = {'start_timestamp': 11, 'end_timestamp': 20,
                         'img_checksum': '6eef5b2dbd2139589774d8c0cf86181724c80a0422d00e8acf5e5815d24c3d96'}
    superuser_change_data = {'start_timestamp': 21}
    invalid_change_data_id = {'id': '95eae770-42f9-4828-878e-23a28bb06439'}
    invalid_change_data_filename = {'img_checksum': valid_change_data['img_checksum']}

    @pytest.mark.dependency()
    async def test_create_menu(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str],
                               valid_create_data: dict[str, Any]):
        await WeekMenu.find().delete()
        response = await http_client.post('/menus', json=valid_create_data, headers=user_w_permissions_headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp['img_checksum'] == valid_create_data['img_checksum']
        assert resp['start_timestamp'] == valid_create_data['start_timestamp']
        assert resp['end_timestamp'] == valid_create_data['end_timestamp']
        assert len(resp['menus']) == 2
        assert resp['menus'][0]['name'] == 'monday'
        assert len(resp['menus'][0]['categories']) == 1
        assert resp['menus'][0]['categories'][0]['name'] == 'test'
        assert len(resp['menus'][0]['categories'][0]['meals']) == 1
        menu = await WeekMenu.get(resp['id'])
        assert menu is not None

    async def test_create_menu_no_headers(self, http_client: AsyncClient, valid_create_data: dict[str, Any]):
        response = await http_client.post('/menus', json=valid_create_data)
        assert response.status_code == 401

    async def test_create_menu_no_permissions(self, http_client: AsyncClient, valid_create_data: dict[str, Any],
                                              user_wo_permissions_headers: dict[str, str]):
        response = await http_client.post('/menus', json=valid_create_data,
                                          headers=user_wo_permissions_headers)
        assert response.status_code == 403

    async def test_create_menu_superuser(self, http_client: AsyncClient, user_superuser_headers: dict[str, str]):
        response = await http_client.post('/menus', json=self.superuser_create_data, headers=user_superuser_headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp['img_checksum'] == self.superuser_create_data['img_checksum']
        assert resp['start_timestamp'] == self.superuser_create_data['start_timestamp']
        assert resp['end_timestamp'] == self.superuser_create_data['end_timestamp']
        assert len(resp['menus']) == 0

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu'])
    async def test_create_menu_duplicate(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str],
                                         valid_create_data: dict[str, Any]):
        count = await WeekMenu.count()
        response = await http_client.post('/menus', json=valid_create_data, headers=user_w_permissions_headers)
        assert response.status_code == 400
        resp = response.json()
        assert resp['detail'] == ErrorCode.MENU_WITH_CHECKSUM_ALREADY_EXISTS
        assert count == await WeekMenu.count()

    @pytest.mark.dependency()
    async def test_create_menu_partial(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str]):
        response = await http_client.post('/menus', json=self.partial_create_data,
                                          headers=user_w_permissions_headers)
        assert response.status_code == 201
        resp = response.json()
        assert resp['img_checksum'] == self.partial_create_data['img_checksum']
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
    async def test_get_menu_by_id(self, http_client: AsyncClient, valid_create_data: dict[str, Any]):
        menu = await WeekMenu.find_one({'img_checksum': valid_create_data['img_checksum']})
        response = await http_client.get(f'/menus/menu/{menu.id}', params={'include_image': True})
        assert response.status_code == 200
        resp = response.json()
        assert str(menu.id) == resp['id']
        assert resp['img'] == valid_create_data['img']
        assert resp['img_checksum'] == valid_create_data['img_checksum']
        assert resp['start_timestamp'] == valid_create_data['start_timestamp']
        assert resp['end_timestamp'] == valid_create_data['end_timestamp']
        assert len(resp['menus']) == 2
        response = await http_client.get(f'/menus/menu/{menu.id}', params={'include_image': False})
        assert response.json()['img'] is None

    async def test_get_menu_by_id_no_result(self, http_client: AsyncClient):
        response = await http_client.get('/menus/menu/95eae770-42f9-4828-878e-23a28bb06439')
        assert response.status_code == 404

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu'])
    async def test_image_by_id(self, http_client: AsyncClient, valid_create_data: dict[str, Any]):
        menu = await WeekMenu.find_one({'img_checksum': valid_create_data['img_checksum']})
        response = await http_client.get(f'/menus/img/{menu.id}')
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/jpeg'
        assert response.content == base64.b64decode(valid_create_data['img'])

    async def test_image_by_id_no_result(self, http_client: AsyncClient):
        response = await http_client.get('/menus/img/95eae770-42f9-4828-878e-23a28bb06439')
        assert response.status_code == 404

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu'])
    async def test_get_menu_by_checksum(self, http_client: AsyncClient, valid_create_data: dict[str, Any]):
        checksum = valid_create_data['img_checksum']
        response = await http_client.get(f'/menus/menu/{checksum}', params={'include_image': True})
        assert response.status_code == 200
        resp = response.json()
        assert resp['img_checksum'] == valid_create_data['img_checksum']
        assert resp['start_timestamp'] == valid_create_data['start_timestamp']
        assert resp['end_timestamp'] == valid_create_data['end_timestamp']
        assert len(resp['menus']) == 2
        response = await http_client.get(f'/menus/menu/{checksum}', params={'include_image': False})
        assert response.json()['img'] is None

    async def test_get_menu_by_checksum_no_result(self, http_client: AsyncClient):
        response = await http_client.get('/menus/menu/43ed77500258a02c127fa7383373e7eff7936761f00fe4b6506af39768e5509e')
        assert response.status_code == 404

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu'])
    async def test_get_image_by_checksum(self, http_client: AsyncClient, valid_create_data: dict[str, Any]):
        checksum = valid_create_data['img_checksum']
        response = await http_client.get(f'/menus/img/{checksum}')
        assert response.status_code == 200
        assert response.headers['content-type'] == 'image/jpeg'
        assert response.content == base64.b64decode(valid_create_data['img'])

    async def test_get_image_by_checksum_no_result(self, http_client: AsyncClient):
        response = await http_client.get('/menus/img/43ed77500258a02c127fa7383373e7eff7936761f00fe4b6506af39768e5509e')
        assert response.status_code == 404

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp_range_all(self, http_client: AsyncClient, valid_create_data: dict[str, Any]):
        response = await http_client.get('/menus', params={'include_image': True})
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) >= 2
        assert any([r['img'] is not None for r in resp])
        assert resp[0]['img_checksum'] == valid_create_data['img_checksum']
        assert resp[1]['img_checksum'] == self.partial_create_data['img_checksum']
        response = await http_client.get('/menus', params={'include_image': False})
        assert all([r['img'] is None for r in response.json()])

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp_range_end(self, http_client: AsyncClient, valid_create_data: dict[str, Any]):
        response = await http_client.get('/menus?end=5')
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 1
        assert resp[0]['img_checksum'] == valid_create_data['img_checksum']

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp_range_start(self, http_client: AsyncClient):
        response = await http_client.get('/menus?start=3')
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == await WeekMenu.count() - 1
        assert resp[0]['img_checksum'] == self.partial_create_data['img_checksum']

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp_range_start_and_stop(self, http_client: AsyncClient):
        response = await http_client.get('/menus?start=3&end=15')
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 1
        assert resp[0]['img_checksum'] == self.partial_create_data['img_checksum']

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp_range_no_results(self, http_client: AsyncClient):
        response = await http_client.get('/menus?start=100')
        assert response.status_code == 200
        resp = response.json()
        assert len(resp) == 0

    @pytest.mark.dependency(depends=['TestMenusRouter::test_create_menu', 'TestMenusRouter::test_create_menu_partial'])
    async def test_get_menu_by_timestamp(self, http_client: AsyncClient, valid_create_data: dict[str, Any]):
        response = await http_client.get('/menus/menu?timestamp=1')
        assert response.status_code == 200
        resp = response.json()
        assert isinstance(resp, dict)
        assert resp['img_checksum'] == valid_create_data['img_checksum']
        response = await http_client.get('/menus/menu?timestamp=7')
        assert response.status_code == 200
        resp = response.json()
        assert isinstance(resp, dict)
        assert resp['img_checksum'] == self.partial_create_data['img_checksum']

    @pytest.mark.dependency()
    async def test_update_menu(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str],
                               rdm_checksums: list[str]):
        menu = WeekMenu(img_checksum=rdm_checksums[0], start_timestamp=11, end_timestamp=20, created_at=11)
        resp = await menu.create()
        assert resp.id is not None
        response = await http_client.patch(f'/menus/menu/{resp.id}', json=self.valid_change_data,
                                           headers=user_w_permissions_headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp['img_checksum'] == self.valid_change_data['img_checksum']
        assert resp['start_timestamp'] == self.valid_change_data['start_timestamp']
        assert resp['end_timestamp'] == self.valid_change_data['end_timestamp']

    async def test_update_menu_no_permissions(self, http_client: AsyncClient,
                                              user_wo_permissions_headers: dict[str, str], rdm_checksums: list[str]):
        menu = WeekMenu(img_checksum=rdm_checksums[0], start_timestamp=11, end_timestamp=20, created_at=11)
        resp = await menu.create()
        assert resp.id is not None
        response = await http_client.patch(f'/menus/menu/{resp.id}', json=self.valid_change_data,
                                           headers=user_wo_permissions_headers)
        assert response.status_code == 403
        menu = await WeekMenu.get(resp.id)
        assert menu.img_checksum == rdm_checksums[0]

    async def test_update_menu_superuser(self, http_client: AsyncClient, user_superuser_headers: dict[str, str],
                                         rdm_checksums: list[str]):
        menu = WeekMenu(img_checksum=rdm_checksums[0], start_timestamp=11, end_timestamp=20, created_at=11)
        resp = await menu.create()
        assert resp.id is not None
        response = await http_client.patch(f'/menus/menu/{resp.id}', json=self.superuser_change_data,
                                           headers=user_superuser_headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp['img_checksum'] == menu.img_checksum
        assert resp['start_timestamp'] == self.superuser_change_data['start_timestamp']
        assert resp['end_timestamp'] == menu.end_timestamp

    async def test_update_menu_id_fail(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str],
                                       rdm_checksums: list[str]):
        menu = WeekMenu(img_checksum=rdm_checksums[0], start_timestamp=11, end_timestamp=20, created_at=11)
        dao = await menu.create()
        assert dao.id is not None
        response = await http_client.patch(f'/menus/menu/{dao.id}', json=self.invalid_change_data_id,
                                           headers=user_w_permissions_headers)
        assert response.status_code == 200
        resp = response.json()
        assert resp['id'] != self.invalid_change_data_id['id']
        assert resp['id'] == str(dao.id)
        assert resp['img_checksum'] == rdm_checksums[0]

    @pytest.mark.dependency(depends=['TestMenusRouter::test_update_menu'])
    async def test_update_menu_filename_fail(self, http_client: AsyncClient,
                                             user_w_permissions_headers: dict[str, str], rdm_checksums: list[str]):
        menu = WeekMenu(img_checksum=rdm_checksums[0], start_timestamp=11, end_timestamp=20, created_at=11)
        dao = await menu.create()
        assert dao.id is not None
        response = await http_client.patch(f'/menus/menu/{dao.id}', json=self.invalid_change_data_filename,
                                           headers=user_w_permissions_headers)
        assert response.status_code == 400
        resp = response.json()
        assert resp['detail'] == ErrorCode.MENU_WITH_CHECKSUM_ALREADY_EXISTS
        dao = await WeekMenu.get(dao.id)
        assert dao.img_checksum == menu.img_checksum

    async def test_delete_menu(self, http_client: AsyncClient, user_w_permissions_headers: dict[str, str],
                               rdm_checksums: list[str]):
        menu = WeekMenu(img_checksum=rdm_checksums[0], start_timestamp=11, end_timestamp=20, created_at=11)
        dao = await menu.create()
        assert dao.id is not None
        response = await http_client.delete(f'/menus/menu/{dao.id}', headers=user_w_permissions_headers)
        assert response.status_code == 204
        assert await WeekMenu.get(dao.id) is None
        response = await http_client.delete(f'/menus/menu/{dao.id}', headers=user_w_permissions_headers)
        assert response.status_code == 404
        assert await WeekMenu.get(dao.id) is None

    async def test_delete_menu_no_permissions(self, http_client: AsyncClient,
                                              user_wo_permissions_headers: dict[str, str], rdm_checksums: list[str]):
        menu = WeekMenu(img_checksum=rdm_checksums[0], start_timestamp=11, end_timestamp=20, created_at=11)
        dao = await menu.create()
        assert dao.id is not None
        response = await http_client.delete(f'/menus/menu/{dao.id}', headers=user_wo_permissions_headers)
        assert response.status_code == 403
        assert await WeekMenu.get(dao.id) is not None

    async def test_delete_menu_superuser(self, http_client: AsyncClient, user_superuser_headers: dict[str, str],
                                         rdm_checksums: list[str]):
        menu = WeekMenu(img_checksum=rdm_checksums[0], start_timestamp=11, end_timestamp=20, created_at=11)
        dao = await menu.create()
        assert dao.id is not None
        response = await http_client.delete(f'/menus/menu/{dao.id}', headers=user_superuser_headers)
        assert response.status_code == 204
        assert await WeekMenu.get(dao.id) is None
        response = await http_client.delete(f'/menus/menu/{dao.id}', headers=user_superuser_headers)
        assert response.status_code == 404
        assert await WeekMenu.get(dao.id) is None
