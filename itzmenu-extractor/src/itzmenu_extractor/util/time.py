from datetime import date, datetime

from holidays.countries import Germany


class CompanyHolidays(Germany):

    def _populate(self, year: int) -> None:
        # Populate the holiday list with the default german holidays
        super()._populate(year)
        if self.subdiv is None:
            self.subdiv = 'SH'
        self[date(year, 12, 24)] = 'Christmas Eve'
        self[date(year, 12, 31)] = "New Year's Eve"


__hdays = CompanyHolidays()


def is_holiday(d: date | datetime | int) -> bool:
    """
    Checks for a given date whether it is a country specific, regional or company holiday.
    :param d: The date to check
    :return: True if the date is a holiday, False otherwise
    """
    if isinstance(d, int):
        d = date.fromtimestamp(d)
    return d in __hdays


def timestamp_to_date(timestamp: int) -> str:
    """
    Converts a unix timestamp to a formatted date string in the format 'dd.mm.yyyy' "
    :param timestamp: The timestamp to convert
    :return: The formatted date string
    """
    return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y')
