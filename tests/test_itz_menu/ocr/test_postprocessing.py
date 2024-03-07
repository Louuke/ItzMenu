import pandas as pd
import pytest

from itz_menu.persistence.models import *


@pytest.fixture()
def week_menu() -> pd.DataFrame:
    df = pd.read_csv('resources/speiseplanWeek.csv')
    df.columns = df.iloc[0].map(lambda x: WeekDay.find_by_value(x), na_action='ignore')
    return df


class TestPostprocessing:

    def test_dataframe_to_week_menu(self, week_menu: pd.DataFrame):
        print(week_menu.index)
