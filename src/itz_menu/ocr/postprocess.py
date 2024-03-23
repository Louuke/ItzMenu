from itz_menu.persistence.models import WeekMenu, DayMenu, MealCategory, Meal
from itz_menu.persistence.enums import DietType
import pandas as pd


def dataframe_to_week_menu(df: pd.DataFrame, validity_period: tuple[int, int], filename: str) -> WeekMenu:
    start_timestamp, end_timestamp = validity_period
    menus = __dataframe_to_menus(df)
    return WeekMenu(start_timestamp=start_timestamp, end_timestamp=end_timestamp, filename=filename, menus=menus)


def __dataframe_to_menus(df: pd.DataFrame) -> list[DayMenu]:
    return [DayMenu(name=day, categories=__dataframe_to_categories(df[day])) for day in df.columns if day is not None]


def __dataframe_to_categories(s: pd.Series):
    def merge_rows(grouped_s: pd.Series):
        return MealCategory(name=grouped_s.index[0], meals=__dataframe_to_meals(grouped_s))
    return s.groupby(s.index).apply(merge_rows).to_list()


def __dataframe_to_meals(s: pd.Series) -> list[Meal]:
    return [Meal(name=s.iloc[i], diet_type=[DietType.UNKNOWN], price=s.iloc[i + 1])
            for i in range(0, len(s), 2) if __validate_meal(s.iloc[i], s.iloc[i + 1])]


def __validate_meal(name: str, price: float) -> bool:
    return not (pd.isna(name) or pd.isna(price)) and name.lower() != 'geschlossen'
