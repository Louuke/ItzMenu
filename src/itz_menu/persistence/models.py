from bunnet import Document, Indexed
from pydantic import BaseModel, Field

from itz_menu.persistence.enums import DietType, WeekDay


class Meal(BaseModel):
    name: str
    diet_type: list[DietType] = Field(default=[])
    price: float = Field(default=float('nan'))


class MealCategory(BaseModel):
    name: str
    meals: list[Meal] = Field(default=[])


class DayMenu(BaseModel):
    name: WeekDay
    categories: list[MealCategory] = Field(default=[])


class WeekMenu(Document):
    start_timestamp: Indexed(int) = Field(ge=0)
    end_timestamp: Indexed(int) = Field(ge=1)
    filename: Indexed(str, unique=True) = Field(pattern=r'^[a-zA-Z0-9]+\.jpg$')
    menus: list[DayMenu] = Field(default=[])

    class Settings:
        name = 'week_menus'
