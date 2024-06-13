import time
from uuid import UUID

import pytest

from itzmenu_api.persistence.enums import WeekDay
from itzmenu_api.persistence.schemas import Meal, MealCategory, DayMenu, WeekMenuCreate, WeekMenuUpdate
from itzmenu_service.manager.exceptions import WeekMenuAlreadyExists, WeekMenuNotExists
from itzmenu_service.manager.menus import WeekMenuManager
from itzmenu_service.persistence.models import WeekMenu


@pytest.mark.asyncio(scope='session')
class TestBaseWeekMenuManager:

    @pytest.mark.dependency()
    async def test_create_success(self, week_menu_manager: WeekMenuManager, rdm_checksums: list[str]):
        meal = Meal(name='test', price=1.0)
        category = MealCategory(name='test', meals=[meal])
        day = DayMenu(name=WeekDay.MONDAY, categories=[category])
        menu = WeekMenuCreate(img_checksum=rdm_checksums[0], start_timestamp=49, end_timestamp=50, menus=[day],
                              img='img')
        result = await week_menu_manager.create_menu(menu)
        assert result.img_checksum == rdm_checksums[0]
        assert result.start_timestamp == 49
        assert result.end_timestamp == 50
        assert len(result.menus) == 1
        assert result.menus[0].name == WeekDay.MONDAY
        assert len(result.menus[0].categories) == 1
        assert result.menus[0].categories[0].name == 'test'
        assert len(result.menus[0].categories[0].meals) == 1
        assert result.menus[0].categories[0].meals[0].name == 'test'

    @pytest.mark.dependency(depends=['TestBaseWeekMenuManager::test_create_success'])
    async def test_create_duplicate(self, week_menu_manager: WeekMenuManager):
        org = await week_menu_manager.get_menu_by_timestamp(49)
        menu = WeekMenuCreate(img_checksum=org.img_checksum, start_timestamp=49, end_timestamp=50)
        with pytest.raises(WeekMenuAlreadyExists):
            await week_menu_manager.create_menu(menu)

    @pytest.mark.dependency()
    async def test_create_override_id(self, week_menu_manager: WeekMenuManager, rdm_checksums: list[str]):
        uuid = '3e96a70a-1928-4f19-811b-3f11be611d2a'
        menu = WeekMenuCreate(id=uuid, img_checksum=rdm_checksums[0], start_timestamp=50, end_timestamp=51)
        result = await week_menu_manager.create_menu(menu)
        assert result.id != uuid
        assert result.img_checksum == rdm_checksums[0]
        assert result.start_timestamp == 50
        assert result.end_timestamp == 51

    async def test_create_missing_fields(self, week_menu_manager: WeekMenuManager, rdm_checksums: list[str]):
        menu = WeekMenuCreate(img_checksum=rdm_checksums[0], start_timestamp=51, end_timestamp=52)
        result = await week_menu_manager.create_menu(menu)
        assert result.img_checksum == rdm_checksums[0]
        assert result.start_timestamp == 51
        assert result.end_timestamp == 52
        assert len(result.menus) == 0
        assert result.created_at > time.time() - 5

    @pytest.mark.dependency(depends=['TestBaseWeekMenuManager::test_create_success'])
    async def test_get_by_id_success_no_img(self, week_menu_manager: WeekMenuManager):
        menu = await WeekMenu.find_one(WeekMenu.start_timestamp == 40 and WeekMenu.end_timestamp == 50)
        result = await week_menu_manager.get_menu_by_id(menu.id)
        assert result.id == menu.id
        assert result.img_checksum == menu.img_checksum
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp
        assert result.img is None

    @pytest.mark.dependency(depends=['TestBaseWeekMenuManager::test_create_success'])
    async def test_get_by_id_success_with_img(self, week_menu_manager: WeekMenuManager):
        menu = await WeekMenu.find_one(WeekMenu.start_timestamp == 40 and WeekMenu.end_timestamp == 50)
        result = await week_menu_manager.get_menu_by_id(menu.id, include_image=True)
        assert result.id == menu.id
        assert result.img_checksum == menu.img_checksum
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp
        assert result.img is not None

    async def test_get_by_id_not_exists(self, week_menu_manager: WeekMenuManager):
        uuid = UUID('3e96a70a-1928-4f19-811b-3f11be611d2a')
        with pytest.raises(WeekMenuNotExists):
            await week_menu_manager.get_menu_by_id(uuid)

    @pytest.mark.dependency(depends=['TestBaseWeekMenuManager::test_create_success'])
    async def test_get_by_checksum_success(self, week_menu_manager: WeekMenuManager):
        menu = await WeekMenu.find_one(WeekMenu.start_timestamp == 40 and WeekMenu.end_timestamp == 50)
        result = await week_menu_manager.get_menu_by_checksum(menu.img_checksum)
        assert result.id == menu.id
        assert result.img_checksum == menu.img_checksum
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp

    async def test_get_by_checksum_not_exists(self, week_menu_manager: WeekMenuManager):
        checksum = 'b24b0dda9cf6ee529c98d1b7492cbee8ed9a924733dab29239a4908f2ac97062'
        with pytest.raises(WeekMenuNotExists):
            await week_menu_manager.get_menu_by_checksum(checksum)

    @pytest.mark.dependency(depends=['TestBaseWeekMenuManager::test_create_success'])
    async def test_get_by_timestamp_success(self, week_menu_manager: WeekMenuManager):
        menu = await WeekMenu.find_one(WeekMenu.start_timestamp == 49 and WeekMenu.end_timestamp == 50)
        result = await week_menu_manager.get_menu_by_timestamp(50)
        assert result.id == menu.id
        assert result.img_checksum == menu.img_checksum
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp

    async def test_get_by_timestamp_not_exists(self, week_menu_manager: WeekMenuManager):
        with pytest.raises(WeekMenuNotExists):
            await week_menu_manager.get_menu_by_timestamp(100)

    @pytest.mark.dependency(depends=['TestBaseWeekMenuManager::test_create_success'])
    async def test_get_by_timestamp_range_success(self, week_menu_manager: WeekMenuManager):
        menu = await WeekMenu.find_one(WeekMenu.start_timestamp == 40 and WeekMenu.end_timestamp == 50)
        result = await week_menu_manager.get_menu_by_timestamp_range(40, 50)
        assert len(result) == 1
        assert result[0].img_checksum == menu.img_checksum

    async def test_get_by_timestamp_range_not_exists(self, week_menu_manager: WeekMenuManager):
        result = await week_menu_manager.get_menu_by_timestamp_range(100, 200)
        assert len(result) == 0

    async def test_update_success(self, week_menu_manager: WeekMenuManager, rdm_checksums: list[str]):
        menu = WeekMenuCreate(img_checksum=rdm_checksums[0], start_timestamp=53, end_timestamp=54)
        menu = await week_menu_manager.create_menu(menu)
        update = WeekMenuUpdate(img='sgusngeop')
        result = await week_menu_manager.update_menu(update, menu)
        assert result.id == menu.id
        assert result.img == update.img
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp

    @pytest.mark.dependency(depends=['TestBaseWeekMenuManager::test_create_success',
                                     'TestBaseWeekMenuManager::test_create_override_id'])
    async def test_update_checksum_fail(self, week_menu_manager: WeekMenuManager):
        menu = await WeekMenu.find(WeekMenu.start_timestamp >= 49 and WeekMenu.end_timestamp <= 51).to_list()
        assert len(menu) == 2
        update = WeekMenuUpdate(img_checksum=menu[0].img_checksum)
        with pytest.raises(WeekMenuAlreadyExists):
            await week_menu_manager.update_menu(update, menu[1])

    async def test_delete_menu(self, week_menu_manager: WeekMenuManager, rdm_checksums: list[str]):
        menu = WeekMenuCreate(img_checksum=rdm_checksums[0], start_timestamp=53, end_timestamp=54)
        menu = await week_menu_manager.create_menu(menu)
        await week_menu_manager.delete_menu(menu)
        assert await WeekMenu.find_one({'id': menu.id}) is None
