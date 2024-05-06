from abc import ABC, abstractmethod


class BaseRequest(ABC):

    @abstractmethod
    def endpoint(self) -> str:
        pass


class WeekMenuRequest(BaseRequest):

    @property
    def endpoint(self) -> str:
        return 'media/img/speiseplanWeek.jpg'


class DayMenuRequest(BaseRequest):

    @property
    def endpoint(self) -> str:
        return 'media/img/speiseplanDay.jpg'
