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

    @staticmethod
    def find_by_value(value: str):
        if value.lower() in ('monday', 'montag'):
            return WeekDay.MONDAY
        elif value.lower() in ('tuesday', 'dienstag'):
            return WeekDay.TUESDAY
        elif value.lower() in ('wednesday', 'mittwoch'):
            return WeekDay.WEDNESDAY
        elif value.lower() in ('thursday', 'donnerstag'):
            return WeekDay.THURSDAY
        elif value.lower() in ('friday', 'freitag'):
            return WeekDay.FRIDAY
