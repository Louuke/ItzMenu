import time

import pytest
from pymongo.errors import DuplicateKeyError

from itzmenu_service.persistence.adapter.adapter import BeanieWeekMenuDatabase
from itzmenu_api.persistence.schemas import WeekMenuCreate, DayMenu, WeekDay, MealCategory, Meal
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
        result = await menu_db.get(menu.id)
        assert result.id == menu.id
        assert result.filename == menu.filename
        assert result.start_timestamp == menu.start_timestamp
        assert result.end_timestamp == menu.end_timestamp

    async def test_get_not_exists(self, menu_db: BeanieWeekMenuDatabase):
        result = await menu_db.get('b0e069e4-2fa1-49cd-a81c-32b34fd3cc66')
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
