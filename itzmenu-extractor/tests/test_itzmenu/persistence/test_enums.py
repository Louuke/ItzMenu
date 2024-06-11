from itzmenu_api.persistence.enums import WeekDay


class TestWeekDay:

    def test_week_day_values(self):
        values = (WeekDay.MONDAY, WeekDay.TUESDAY, WeekDay.WEDNESDAY, WeekDay.THURSDAY, WeekDay.FRIDAY)
        assert WeekDay.values() == values

    def test_week_day_find_by_value(self):
        assert WeekDay.find_by_value('monday') == WeekDay.MONDAY
        assert WeekDay.find_by_value('Montag') == WeekDay.MONDAY
        assert WeekDay.find_by_value('tuesday') == WeekDay.TUESDAY
        assert WeekDay.find_by_value('Dienstag') == WeekDay.TUESDAY
        assert WeekDay.find_by_value('wednesday') == WeekDay.WEDNESDAY
        assert WeekDay.find_by_value('Mittwoch') == WeekDay.WEDNESDAY
        assert WeekDay.find_by_value('thursday') == WeekDay.THURSDAY
        assert WeekDay.find_by_value('Donnerstag') == WeekDay.THURSDAY
        assert WeekDay.find_by_value('friday') == WeekDay.FRIDAY
        assert WeekDay.find_by_value('Freitag') == WeekDay.FRIDAY
