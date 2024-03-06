import requests
import logging as log

from .requests import BaseRequest, WeekMenuRequest


class MenuClient:

    def __init__(self, host: str = 'https://ivi.de'):
        self.__session = requests.Session()
        self.__host = host

    def __del__(self):
        self.__session.close()

    def get_week_menu(self) -> bytes | None:
        return self.__request(WeekMenuRequest())

    def __request(self, request: BaseRequest) -> bytes | None:
        try:
            url = f'{self.__host}/{request.endpoint}'
            response = self.__session.get(url)
            response.raise_for_status()
            return response.content
        except requests.ConnectionError as exc:
            log.error(f'An error occurred while requesting {exc.request.url!r}.')
        except requests.HTTPError as exc:
            log.error(f'Error response {exc.response.status_code} while requesting {exc.request.url!r}.')
