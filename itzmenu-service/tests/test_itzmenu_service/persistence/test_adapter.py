import pytest

from itzmenu_service.persistence.adapter.adapter import BeanieWeekMenuDatabase
from itzmenu_api.persistence.schemas import WeekMenuCreate, DayMenu, WeekDay, MealCategory, Meal


@pytest.mark.asyncio(scope='session')
class TestBaseWeekMenuDatabase:

    @pytest.mark.dependency()
    async def test_create_success(self, menu_db: BeanieWeekMenuDatabase):
        meal = Meal(name='test', price=1.0)
        category = MealCategory(name='test', meals=[meal])
        day = DayMenu(name=WeekDay.MONDAY, categories=[category])
        menu = WeekMenuCreate(filename='test.jpg', start_timestamp=1, end_timestamp=5, menus=[day])
        create = menu.create_update_dict()
        result = await menu_db.create(create)
        assert result.id is not None
        assert result.filename == 'test.jpg'
        assert result.start_timestamp == 1
        assert result.end_timestamp == 5
        assert len(result.menus) == 1
        assert result.menus[0].name == WeekDay.MONDAY
        assert len(result.menus[0].categories) == 1
        assert result.menus[0].categories[0].name == 'test'
        assert len(result.menus[0].categories[0].meals) == 1
        assert result.menus[0].categories[0].meals[0].name == 'test'
