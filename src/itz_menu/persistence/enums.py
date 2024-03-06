from enum import StrEnum


class DietType(StrEnum):
    MIXED = 'mixed',
    VEGETARIANISM = 'vegetarianism',
    VEGANISM = 'veganism',
    PESCETARIANISM = 'pescetarianism',
    UNKNOWN = 'unknown'


class WeekDay(StrEnum):
    MONDAY = 'monday',
    TUESDAY = 'tuesday',
    WEDNESDAY = 'wednesday',
    THURSDAY = 'thursday',
    FRIDAY = 'friday'
