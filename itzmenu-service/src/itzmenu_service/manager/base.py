from typing import Generic, Optional

from fastapi import Request, Response
from fastapi_users.models import ID

from itzmenu_api.persistence.schemas import CreateWeekMenu
from itzmenu_service.manager import exceptions
from itzmenu_service.persistence.adapter.base import BaseWeekMenuDatabase
from itzmenu_service.persistence.models import WeekMenu


class BaseWeekMenuManager(Generic[ID]):
    """
    Week menu management logic.

    :param menu_db: Database adapter instance.
    """

    menu_db: BaseWeekMenuDatabase[ID]

    def __init__(self, menu_db: BaseWeekMenuDatabase[ID]):
        self.menu_db = menu_db

    async def get(self, id: ID) -> WeekMenu:
        """
        Get a week menu by id.

        :param id: Id. of the week menu to retrieve.
        :raises WeekMenuNotExists: The week menu does not exist.
        :return: A week menu.
        """
        if (menu := await self.menu_db.get(id)) is None:
            raise exceptions.WeekMenuNotExists()
        return menu

    async def get_by_filename(self, filename: str) -> WeekMenu:
        """
        Get a week menu by filename.

        :param filename: Filename of the week menu to retrieve.
        :raises WeekMenuNotExists: The week menu does not exist.
        :return: A week menu.
        """
        if (menu := await self.menu_db.get_by_filename(filename)) is None:
            raise exceptions.WeekMenuNotExists()
        return menu

    async def create(self, menu_create: CreateWeekMenu, request: Optional[Request] = None) -> WeekMenu:
        """
        Create a week menu in database.

        Triggers the on_after_new_menu handler on success.

        :param menu_create: The CreateWeekMenu model to create.
        :param request: Optional FastAPI request that triggered the operation, defaults to None.
        :raises WeekMenuAlreadyExists: A user already exists with the same e-mail.
        :return: A new week menu.
        """
        existing_menu = await self.menu_db.get_by_filename(menu_create.filename)
        if existing_menu is not None:
            raise exceptions.WeekMenuAlreadyExists()

        menu_dict = menu_create.create_update_dict()
        created_menu = await self.menu_db.create(menu_dict)
        await self.on_after_new_menu(created_menu, request)
        return created_menu

    async def on_after_new_menu(self, menu: WeekMenu, request: Optional[Request] = None) -> None:
        """
        Perform logic after successful week menu creation.

        :param menu: The created week menu.
        :param request: Optional FastAPI request that triggered the operation, defaults to None.
        """
        return
