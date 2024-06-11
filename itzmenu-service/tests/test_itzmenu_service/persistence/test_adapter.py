import time

import pytest
from beanie.exceptions import RevisionIdWasChanged
from pymongo.errors import DuplicateKeyError

from itzmenu_service.persistence.adapter.adapter import BeanieWeekMenuDatabase
from itzmenu_api.persistence.schemas import WeekMenuCreate, WeekMenuUpdate, DayMenu, WeekDay, MealCategory, Meal
from itzmenu_service.persistence.models import WeekMenu


@pytest.mark.asyncio(scope='session')
class TestBaseWeekMenuDatabase:

    @pytest.mark.dependency()
    async def test_create_success(self, menu_db: BeanieWeekMenuDatabase, rdm_checksums: list[str]):
        meal = Meal(name='test', price=1.0)
        category = MealCategory(name='test', meals=[meal])
        day = DayMenu(name=WeekDay.MONDAY, categories=[category])
        menu = WeekMenuCreate(img_checksum=rdm_checksums[0], start_timestamp=1, end_timestamp=5, menus=[day])
        create = menu.create_update_dict()
        result = await menu_db.create(create)
        assert result.id is not None
        assert result.img_checksum == rdm_checksums[0]
        assert result.start_timestamp == 1
        assert result.end_timestamp == 5
        assert len(result.menus) == 1
        assert result.menus[0].name == WeekDay.MONDAY
        assert len(result.menus[0].categories) == 1
        assert result.menus[0].categories[0].name == 'test'
        assert len(result.menus[0].categories[0].meals) == 1
        assert result.menus[0].categories[0].meals[0].name == 'test'

    @pytest.mark.dependency(depends=['TestBaseWeekMenuDatabase::test_create_success'])
    async def test_create_duplicate(self, menu_db: BeanieWeekMenuDatabase):
        org = await WeekMenu.find_one()
        menu = WeekMenuCreate(img_checksum=org.img_checksum, start_timestamp=1, end_timestamp=5)
        create = menu.create_update_dict()
        with pytest.raises(DuplicateKeyError):
            await menu_db.create(create)

    async def test_create_missing_fields(self, menu_db: BeanieWeekMenuDatabase, rdm_checksums: list[str]):
        menu = WeekMenuCreate(img_checksum=rdm_checksums[0], start_timestamp=2, end_timestamp=10)
        create = menu.create_update_dict()
        result = await menu_db.create(create)
        assert result.id is not None
        assert result.img_checksum == rdm_checksums[0]
        assert result.start_timestamp == 2
        assert result.end_timestamp == 10
        assert len(result.menus) == 0
        assert result.created_at > time.time() - 5

    @pytest.mark.dependency(depends=['TestBaseWeekMenuDatabase::test_create_success'])
    async def test_get_success(self, menu_db: BeanieWeekMenuDatabase):
        menu = await WeekMenu.find_one()
        result = await menu_db.get_by_id(menu.id)
        assert result.id == menu.id
        assert result.img_checksum == menu.img_checksum
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp

    async def test_get_not_exists(self, menu_db: BeanieWeekMenuDatabase):
        result = await menu_db.get_by_id('b0e069e4-2fa1-49cd-a81c-32b34fd3cc66')
        assert result is None

    @pytest.mark.dependency(depends=['TestBaseWeekMenuDatabase::test_create_success'])
    async def test_get_by_checksum_success(self, menu_db: BeanieWeekMenuDatabase):
        menu = await WeekMenu.find_one()
        result = await menu_db.get_by_image(menu.img_checksum)
        assert result.id == menu.id
        assert result.img_checksum == menu.img_checksum
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp

    async def test_get_by_checksum_not_exists(self, menu_db: BeanieWeekMenuDatabase):
        result = await menu_db.get_by_image('b24b0dda9cf6ee529c98d1b7492cbee8ed9a924733dab29239a4908f2ac97062')
        assert result is None

    @pytest.mark.dependency(depends=['TestBaseWeekMenuDatabase::test_create_success'])
    async def test_get_by_timestamp_success(self, menu_db: BeanieWeekMenuDatabase):
        menu = await WeekMenu.find_one()
        result = await menu_db.get_by_timestamp(menu.start_timestamp)
        assert result.id == menu.id
        assert result.img_checksum == menu.img_checksum
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp

    async def test_get_by_timestamp_not_exists(self, menu_db: BeanieWeekMenuDatabase):
        result = await menu_db.get_by_timestamp(100)
        assert result is None

    @pytest.mark.dependency(depends=['TestBaseWeekMenuDatabase::test_create_success'])
    async def test_get_by_timestamp_range_success(self, menu_db: BeanieWeekMenuDatabase):
        menu = await WeekMenu.find_one({'start_timestamp': 1, 'end_timestamp': 5})
        result = await menu_db.get_by_timestamp_range(1, 5)
        assert len(result) == 1
        assert result[0].img_checksum == menu.img_checksum

    async def test_get_by_timestamp_range_not_exists(self, menu_db: BeanieWeekMenuDatabase):
        result = await menu_db.get_by_timestamp_range(100, 200)
        assert len(result) == 0

    async def test_update_success(self, menu_db: BeanieWeekMenuDatabase, rdm_checksums: list[str]):
        menu = WeekMenuCreate(img_checksum=rdm_checksums[0], start_timestamp=2, end_timestamp=10, created_at=3)
        create = menu.create_update_dict()
        result = await menu_db.create(create)
        assert len(result.menus) == 0
        day = DayMenu(name=WeekDay.MONDAY)
        update = WeekMenuUpdate(img_checksum=rdm_checksums[1], start_timestamp=3, end_timestamp=11, created_at=4,
                                menus=[day])
        update_dict = update.create_update_dict()
        updated = await menu_db.update(result, update_dict)
        assert updated.id == result.id
        assert updated.img_checksum == rdm_checksums[1]
        assert updated.start_timestamp == 3
        assert updated.end_timestamp == 11
        assert updated.created_at == 4
        assert len(updated.menus) == 1

    @pytest.mark.dependency(depends=['TestBaseWeekMenuDatabase::test_create_success'])
    async def test_update_id_fail(self, menu_db: BeanieWeekMenuDatabase):
        menu = await WeekMenu.find_one()
        update = WeekMenuUpdate(id='b0e069e4-2fa1-49cd-a81c-32b34fd3cc66')
        update_dict = update.create_update_dict()
        updated_menu = await menu_db.update(menu, update_dict)
        assert updated_menu.id == menu.id

    @pytest.mark.dependency(depends=['TestBaseWeekMenuDatabase::test_create_success'])
    async def test_update_checksum_fail(self, menu_db: BeanieWeekMenuDatabase, rdm_checksums: list[str]):
        org = await WeekMenu.find_one({'start_timestamp': 1, 'end_timestamp': 5})
        menu = WeekMenuCreate(img_checksum=rdm_checksums[0], start_timestamp=2, end_timestamp=10)
        create = menu.create_update_dict()
        menu = await menu_db.create(create)
        update = WeekMenuUpdate(img_checksum=org.img_checksum)
        update_dict = update.create_update_dict()
        with pytest.raises(RevisionIdWasChanged):
            await menu_db.update(menu, update_dict)

    async def test_delete_success(self, menu_db: BeanieWeekMenuDatabase, rdm_checksums: list[str]):
        menu = WeekMenuCreate(img_checksum=rdm_checksums[0], start_timestamp=2, end_timestamp=10)
        create = menu.create_update_dict()
        result = await menu_db.create(create)
        uid = result.id
        result = await menu_db.delete(result)
        assert result
        assert await WeekMenu.find_one({'id': uid}) is None

    async def test_count(self, menu_db: BeanieWeekMenuDatabase, rdm_checksums: list[str]):
        count = await menu_db.count()
        menu = WeekMenuCreate(img_checksum=rdm_checksums[0], start_timestamp=2, end_timestamp=10)
        create = menu.create_update_dict()
        await menu_db.create(create)
        assert await menu_db.count() == count + 1
