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
    async def test_create_success(self, menu_db: BeanieWeekMenuDatabase):
        meal = Meal(name='test', price=1.0)
        category = MealCategory(name='test', meals=[meal])
        day = DayMenu(name=WeekDay.MONDAY, categories=[category])
        menu = WeekMenuCreate(filename='test1.jpg', start_timestamp=1, end_timestamp=5, menus=[day])
        create = menu.create_update_dict()
        result = await menu_db.create(create)
        assert result.id is not None
        assert result.filename == 'test1.jpg'
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
        menu = WeekMenuCreate(filename='test1.jpg', start_timestamp=1, end_timestamp=5)
        create = menu.create_update_dict()
        with pytest.raises(DuplicateKeyError):
            await menu_db.create(create)

    async def test_create_missing_fields(self, menu_db: BeanieWeekMenuDatabase):
        menu = WeekMenuCreate(filename='test2.jpg', start_timestamp=2, end_timestamp=10)
        create = menu.create_update_dict()
        result = await menu_db.create(create)
        assert result.id is not None
        assert result.filename == 'test2.jpg'
        assert result.start_timestamp == 2
        assert result.end_timestamp == 10
        assert len(result.menus) == 0
        assert result.created_at > time.time() - 5

    @pytest.mark.dependency(depends=['TestBaseWeekMenuDatabase::test_create_success'])
    async def test_get_success(self, menu_db: BeanieWeekMenuDatabase):
        menu = await WeekMenu.find_one()
        result = await menu_db.get_by_id(menu.id)
        assert result.id == menu.id
        assert result.filename == menu.filename
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp

    async def test_get_not_exists(self, menu_db: BeanieWeekMenuDatabase):
        result = await menu_db.get_by_id('b0e069e4-2fa1-49cd-a81c-32b34fd3cc66')
        assert result is None

    @pytest.mark.dependency(depends=['TestBaseWeekMenuDatabase::test_create_success'])
    async def test_get_by_filename_success(self, menu_db: BeanieWeekMenuDatabase):
        menu = await WeekMenu.find_one()
        result = await menu_db.get_by_filename(menu.filename)
        assert result.id == menu.id
        assert result.filename == menu.filename
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp

    async def test_get_by_filename_not_exists(self, menu_db: BeanieWeekMenuDatabase):
        result = await menu_db.get_by_filename('test3.jpg')
        assert result is None

    @pytest.mark.dependency(depends=['TestBaseWeekMenuDatabase::test_create_success'])
    async def test_get_by_timestamp_success(self, menu_db: BeanieWeekMenuDatabase):
        menu = await WeekMenu.find_one()
        result = await menu_db.get_by_timestamp(menu.start_timestamp)
        assert result.id == menu.id
        assert result.filename == menu.filename
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp

    async def test_get_by_timestamp_not_exists(self, menu_db: BeanieWeekMenuDatabase):
        result = await menu_db.get_by_timestamp(100)
        assert result is None

    @pytest.mark.dependency(depends=['TestBaseWeekMenuDatabase::test_create_success'])
    async def test_get_by_timestamp_range_success(self, menu_db: BeanieWeekMenuDatabase):
        result = await menu_db.get_by_timestamp_range(1, 5)
        assert len(result) == 1
        assert result[0].filename == 'test1.jpg'

    async def test_get_by_timestamp_range_not_exists(self, menu_db: BeanieWeekMenuDatabase):
        result = await menu_db.get_by_timestamp_range(100, 200)
        assert len(result) == 0

    async def test_update_success(self, menu_db: BeanieWeekMenuDatabase):
        menu = WeekMenuCreate(filename='test3.jpg', start_timestamp=2, end_timestamp=10, created_at=3)
        create = menu.create_update_dict()
        result = await menu_db.create(create)
        assert len(result.menus) == 0
        day = DayMenu(name=WeekDay.MONDAY)
        update = WeekMenuUpdate(filename='test4.jpg', start_timestamp=3, end_timestamp=11, created_at=4, menus=[day])
        update_dict = update.create_update_dict()
        updated = await menu_db.update(result, update_dict)
        assert updated.id == result.id
        assert updated.filename == 'test4.jpg'
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
    async def test_update_filename_fail(self, menu_db: BeanieWeekMenuDatabase):
        menu = WeekMenuCreate(filename='test5.jpg', start_timestamp=2, end_timestamp=10)
        create = menu.create_update_dict()
        menu = await menu_db.create(create)
        update = WeekMenuUpdate(filename='test1.jpg')
        update_dict = update.create_update_dict()
        with pytest.raises(RevisionIdWasChanged):
            await menu_db.update(menu, update_dict)

    async def test_delete_success(self, menu_db: BeanieWeekMenuDatabase):
        menu = WeekMenuCreate(filename='test6.jpg', start_timestamp=2, end_timestamp=10)
        create = menu.create_update_dict()
        result = await menu_db.create(create)
        uid = result.id
        result = await menu_db.delete(result)
        assert result
        assert await WeekMenu.find_one({'id': uid}) is None

    async def test_count(self, menu_db: BeanieWeekMenuDatabase):
        count = await menu_db.count()
        menu = WeekMenuCreate(filename='test7.jpg', start_timestamp=2, end_timestamp=10)
        create = menu.create_update_dict()
        await menu_db.create(create)
        assert await menu_db.count() == count + 1
