import asyncio

import pandas as pd
import pytest

import itzmenu.persistence.database as database
import itzmenu.ocr.postprocess as postprocess

from itzmenu.persistence.models import *


@pytest.fixture()
def week_menu() -> pd.DataFrame:
    df = pd.read_csv('tests/resources/speiseplanWeek.csv')
    df.columns = df.columns.map(lambda x: WeekDay.find_by_value(x), na_action='ignore')
    df.set_index(df.columns[0], inplace=True)
    return df


@pytest.fixture(scope='session')
def init_database():
    asyncio.run(database.init())


class TestPostprocessing:

    def test_dataframe_to_week_menu_validity_period(self, week_menu: pd.DataFrame, init_database):
        validity_period = (1708297200, 1708729199)
        menu = postprocess.dataframe_to_week_menu(week_menu, validity_period, 'checksum.jpg')
        assert menu.start_timestamp == validity_period[0]
        assert menu.end_timestamp == validity_period[1]

    def test_dataframe_to_week_menu_filename(self, week_menu: pd.DataFrame, init_database):
        filename = 'checksum.jpg'
        menu = postprocess.dataframe_to_week_menu(week_menu, (0, 1), filename)
        assert menu.filename == filename

    def test_dataframe_to_week_menu_menus(self, week_menu: pd.DataFrame, init_database):
        menu = postprocess.dataframe_to_week_menu(week_menu, (0, 1), 'checksum.jpg')
        assert len(menu.menus) == 5
        assert all(isinstance(day, DayMenu) for day in menu.menus)

    def test_dataframe_to_week_menu_day_menu(self, week_menu: pd.DataFrame, init_database):
        menu = postprocess.dataframe_to_week_menu(week_menu, (0, 1), 'checksum.jpg')
        assert all(day.name in WeekDay for day in menu.menus)
        assert tuple([day.name for day in menu.menus]) == WeekDay.values()
        assert all(len(day.categories) == 5 for day in menu.menus)
        assert all(isinstance(category, MealCategory) for day in menu.menus for category in day.categories)

    def test_dataframe_to_week_menu_meal_category(self, week_menu: pd.DataFrame, init_database):
        menu = postprocess.dataframe_to_week_menu(week_menu, (0, 1), 'checksum.jpg')
        categories = ('Suppe', 'Heimatküche', 'From the Bowl', 'Front Cooking', 'Naschglück')
        assert all(category.name in categories for day in menu.menus for category in day.categories)
        assert all(len(category.meals) in (1, 2) for day in menu.menus for category in day.categories)
        assert all(isinstance(meal, Meal) for d in menu.menus for category in d.categories for meal in category.meals)

    def test_dataframe_to_week_menu_meal(self, week_menu: pd.DataFrame, init_database):
        menu = postprocess.dataframe_to_week_menu(week_menu, (0, 1), 'checksum.jpg')
        assert all(len(meal.name) > 5 for d in menu.menus for category in d.categories for meal in category.meals)
        assert all(meal.price >= 0 for d in menu.menus for category in d.categories for meal in category.meals)
        assert all(isinstance(meal.diet_type, list) for d in menu.menus for c in d.categories for meal in c.meals)
