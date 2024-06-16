from pathlib import Path

import pandas as pd
import pytest

import itzmenu_extractor.ocr.postprocess as postprocess

from itzmenu_api.persistence.schemas import WeekDay, DayMenu, MealCategory, Meal


@pytest.fixture()
def week_menu_df(week_menu_csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(week_menu_csv_path)
    df.columns = df.columns.map(lambda x: WeekDay.find_by_value(x), na_action='ignore')
    df.set_index(df.columns[0], inplace=True)
    return df


class TestPostprocessing:

    def test_dataframe_to_week_menu_validity_period(self, week_menu_df: pd.DataFrame, week_menu_checksum: str):
        validity_period = (1708297200, 1708729199)
        menu = postprocess.dataframe_to_week_menu(week_menu_df, validity_period, week_menu_checksum, None)
        assert menu.start_timestamp == validity_period[0]
        assert menu.end_timestamp == validity_period[1]

    def test_dataframe_to_week_menu_checksum(self, week_menu_df: pd.DataFrame, week_menu_checksum: str):
        menu = postprocess.dataframe_to_week_menu(week_menu_df, (0, 1), week_menu_checksum, None)
        assert menu.img_checksum == week_menu_checksum

    def test_dataframe_to_week_menu_menus(self, week_menu_df: pd.DataFrame, week_menu_checksum: str):
        menu = postprocess.dataframe_to_week_menu(week_menu_df, (0, 1), week_menu_checksum, None)
        assert len(menu.menus) == 5
        assert all(isinstance(day, DayMenu) for day in menu.menus)

    def test_dataframe_to_week_menu_day_menu(self, week_menu_df: pd.DataFrame, week_menu_checksum: str):
        menu = postprocess.dataframe_to_week_menu(week_menu_df, (0, 1), week_menu_checksum, None)
        assert all(day.name in WeekDay for day in menu.menus)
        assert [day.name for day in menu.menus] == WeekDay.values()
        assert all(len(day.categories) == 5 for day in menu.menus)
        assert all(isinstance(category, MealCategory) for day in menu.menus for category in day.categories)

    def test_dataframe_to_week_menu_meal_category(self, week_menu_df: pd.DataFrame, week_menu_checksum: str):
        menu = postprocess.dataframe_to_week_menu(week_menu_df, (0, 1), week_menu_checksum, None)
        categories = ('Suppe', 'Heimatküche', 'From the Bowl', 'Front Cooking', 'Naschglück')
        assert all(category.name in categories for day in menu.menus for category in day.categories)
        assert all(len(category.meals) in (1, 2) for day in menu.menus for category in day.categories)
        assert all(isinstance(meal, Meal) for d in menu.menus for category in d.categories for meal in category.meals)

    def test_dataframe_to_week_menu_meal(self, week_menu_df: pd.DataFrame, week_menu_checksum: str):
        menu = postprocess.dataframe_to_week_menu(week_menu_df, (0, 1), week_menu_checksum, None)
        assert all(len(meal.name) > 5 for d in menu.menus for category in d.categories for meal in category.meals)
        assert all(meal.price >= 0 for d in menu.menus for category in d.categories for meal in category.meals)
        assert all(isinstance(meal.curated_diet_type, list) for d in menu.menus for c in d.categories
                   for meal in c.meals)
