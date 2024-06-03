from uuid import UUID

import requests

from itzmenu_api.persistence.schemas import WeekMenuCreate, WeekMenuRead


def retry_request(attempts: int = 1):
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            for _ in range(max(attempts, 1)):
                if (response := func(self, *args, **kwargs)).ok:
                    return response
                elif response.status_code == requests.codes.unauthorized:
                    self._refresh_access_token()
            else:
                response.raise_for_status()
            return response

        return wrapper

    return decorator


class ItzMenuClient:

    def __init__(self, email: str, password: str, host: str | None = 'http://localhost:8000'):
        self.__session = requests.Session()
        self.__email = email
        self.__password = password
        self.__host = host

    def __del__(self):
        self.__session.close()

    def create_menu(self, menu: WeekMenuCreate) -> WeekMenuRead:
        data = menu.create_update_dict()
        req = requests.Request('POST', f'{self.__host}/menus', json=data)
        res = self.__execute_request(req).json()
        return WeekMenuRead(**res)

    def get_menu_by_id(self, menu_id: str | UUID) -> WeekMenuRead:
        req = requests.Request('GET', f'{self.__host}/menus/menu/{menu_id}')
        res = self.__execute_request(req).json()
        return WeekMenuRead(**res)

    def get_menu_by_timestamp(self, timestamp: int) -> WeekMenuRead:
        req = requests.Request('GET', f'{self.__host}/menus/menu?timestamp={timestamp}')
        res = self.__execute_request(req).json()
        return WeekMenuRead(**res)

    def _refresh_access_token(self):
        if (response := self._login()).ok and response.headers['content-type'] == 'application/json':
            token = response.json()['access_token']
            self.__session.headers.update({'Authorization': f'Bearer {token}'})

    def _login(self) -> requests.Response:
        data = {'username': self.__email, 'password': self.__password}
        req = requests.Request('POST', f'{self.__host}/auth/login', data=data)
        return self.__execute_request(req)

    @retry_request(attempts=3)
    def __execute_request(self, request: requests.Request) -> requests.Response:
        prepped = self.__session.prepare_request(request)
        return self.__session.send(prepped, timeout=5)
