import itz_menu.persistence.database as database
from itz_menu import Settings
from itz_menu.persistence.models import Meal, WeekMenu, DayMenu, MealCategory
from itz_menu.persistence.enums import DietType, WeekDay


def _init():
    database.init(Settings())
    WeekMenu.delete_all()
    meal = Meal(name='test', price=1.0, diet_type=[DietType.PESCETARIANISM])
    day_menu = DayMenu(name=WeekDay.MONDAY, categories=[MealCategory(name='test', meals=[meal])])
    menu = WeekMenu(filename='sijfeus.jpg', start_timestamp=1709329098, end_timestamp=1709329098, menus=[day_menu])
    menu.insert()
    assert WeekMenu.find_one(WeekMenu.filename == 'sijfeus.jpg') is not None
