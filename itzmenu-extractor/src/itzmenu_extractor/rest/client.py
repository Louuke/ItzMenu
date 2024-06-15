import requests
import logging as log

import itzmenu_extractor.util.env as env
from itzmenu_extractor.rest.requests import BaseRequest, WeekMenuRequest


class MenuClient:

    def __init__(self, host: str | None = None):
        self.__session = requests.Session()
        self.__host = host if host is not None else 'https://ivi.de'

    def __del__(self):
        self.__session.close()

    def get_week_menu(self) -> bytes | None:
        return self.__request(WeekMenuRequest())

    def __request(self, request: BaseRequest) -> bytes | None:
        try:
            url = f'{self.__host}/{request.endpoint}'
            response = self.__session.get(url, allow_redirects=False)
            response.raise_for_status()
            return response.content
        except requests.ConnectionError as exc:
            log.error(f'An error occurred while requesting {exc.request.url!r}.')
        except requests.HTTPError as exc:
            log.error(f'Error response {exc.response.status_code} while requesting {exc.request.url!r}.')
