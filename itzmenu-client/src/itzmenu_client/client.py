from typing import Callable
from uuid import UUID

import requests
import logging as log

from itzmenu_api.persistence.schemas import WeekMenuCreate, WeekMenuRead, WeekMenuUpdate


def retry_request(attempts: int = 1) -> Callable:
    """
    Decorator to retry a request a given number of times.
    :param attempts: Number of attempts to retry the request.
    :return: The response of the request.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            for _ in range(max(attempts, 1)):
                if (response := func(self, *args, **kwargs)).ok:
                    return response
                elif response.status_code == requests.codes.unauthorized:
                    self._refresh_access_token()
            else:
                log.error(f'Failed to execute http request: {response.url}')
                log.error(f'Response status code: {response.status_code}')
                log.error(f'Response content: {response.content}')
                return None

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

    def create_menu(self, menu: WeekMenuCreate) -> WeekMenuRead | None:
        """
        Create a week menu.
        :param menu: An instance of WeekMenuCreate containing the data for the week menu.
        :return: The created week menu.
        """
        data = menu.create_update_dict()
        req = requests.Request('POST', f'{self.__host}/menus', json=data)
        resp = self.__execute_request(req)
        return WeekMenuRead(**resp.json()) if resp is not None and resp.ok else None

    def get_menu_by_id_or_filename(self, menu_id_or_checksum: str | UUID) -> WeekMenuRead | None:
        """
        Get a week menu by its id or checksum.
        :param menu_id_or_checksum: The id or checksum of the week menu.
        :return: The week menu.
        """
        req = requests.Request('GET', f'{self.__host}/menus/menu/{menu_id_or_checksum}')
        resp = self.__execute_request(req)
        return WeekMenuRead(**resp.json()) if resp is not None and resp.ok else None

    def get_menu_by_timestamp(self, timestamp: int) -> WeekMenuRead | None:
        """
        Get a week menu by timestamp.
        :param timestamp: The timestamp of the week menu.
        :return: The week menu.
        """
        req = requests.Request('GET', f'{self.__host}/menus/menu?timestamp={timestamp}')
        resp = self.__execute_request(req)
        return WeekMenuRead(**resp.json()) if resp is not None and resp.ok else None

    def get_menu_by_timestamp_range(self, start: int = 0, end: int = 9999999999) -> list[WeekMenuRead]:
        """
        Get a list of week menus by timestamp range.
        :param start: Start of the timestamp range.
        :param end: End of the timestamp range.
        :return: A list of week menus.
        """
        req = requests.Request('GET', f'{self.__host}/menus?start={start}&end={end}')
        resp = self.__execute_request(req)
        return [WeekMenuRead(**menu) for menu in resp.json()] if resp is not None and resp.ok else []

    def update_menu(self, menu_id_or_checksum: str | UUID, menu: WeekMenuUpdate) -> WeekMenuRead | None:
        """
        Update a menu by its id or checksum.
        :param menu_id_or_checksum: The id or checksum of the menu to update.
        :param menu: An instance of WeekMenuUpdate containing the updated data.
        :return: The updated menu.
        """
        data = menu.create_update_dict()
        req = requests.Request('PATCH', f'{self.__host}/menus/menu/{menu_id_or_checksum}', json=data)
        resp = self.__execute_request(req)
        return WeekMenuRead(**resp.json()) if resp is not None and resp.ok else None

    def delete_menu(self, menu_id_or_checksum: str | UUID) -> bool:
        """
        Delete a menu by its id or checksum.
        :param menu_id_or_checksum: The id or checksum of the menu to delete.
        :return: True if the menu was deleted, False otherwise.
        """
        req = requests.Request('DELETE', f'{self.__host}/menus/menu/{menu_id_or_checksum}')
        return (resp := self.__execute_request(req)) is not None and resp.ok

    def _refresh_access_token(self):
        if (response := self._login()) is not None and response.ok:
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
