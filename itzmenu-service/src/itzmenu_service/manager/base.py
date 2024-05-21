from typing import Generic, Optional, Any

from fastapi import Request
from fastapi_users.models import ID
from fastapi_users.types import DependencyCallable

from itzmenu_api.persistence.schemas import WeekMenuCreate, WeekMenuRead
from itzmenu_service.manager import exceptions
from itzmenu_service.persistence.adapter.base import BaseWeekMenuDatabase
from itzmenu_service.persistence.models import WeekMenu


class BaseWeekMenuManager(Generic[ID]):
    """
    Week menu management logic.

    :param menu_db: Database adapter instance.
    """

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

    async def get_by_timestamp(self, timestamp: int) -> WeekMenu:
        """
        Get a week menu by timestamp.

        :param timestamp: Timestamp of the week menu to retrieve.
        :raises WeekMenuNotExists: No week menu exists for the given timestamp.
        :return: A week menu.
        """
        if (menu := await self.menu_db.get_by_timestamp(timestamp)) is None:
            raise exceptions.WeekMenuNotExists()
        return menu

    async def create(self, menu_create: WeekMenuCreate, request: Optional[Request] = None) -> WeekMenu:
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
        await self.on_after_create(created_menu, request)
        return created_menu

    async def update(self, menu_update: WeekMenuRead, menu: WeekMenu, request: Optional[Request] = None) -> WeekMenu:
        """
        Update a week menu.

        Triggers the on_after_update handler on success

        :param menu_update: The UserUpdate model containing
        the changes to apply to the user.
        :param menu: The current week menu to update.
        :param request: Optional FastAPI request that triggered the operation, defaults to None.
        :return: The updated week menu.
        """
        updated_menu_data = menu_update.create_update_dict()
        updated_menu = await self._update(menu, updated_menu_data)
        await self.on_after_update(updated_menu, updated_menu_data, request)
        return updated_menu

    async def delete(self, menu: WeekMenu, request: Optional[Request] = None) -> None:
        """
        Delete a user.

        :param menu: The week menu to delete.
        :param request: Optional FastAPI request that triggered the operation, defaults to None.
        """
        await self.on_before_delete(menu, request)
        await self.menu_db.delete(menu)
        await self.on_after_delete(menu, request)

    async def on_after_create(self, menu: WeekMenu, request: Optional[Request] = None):
        """
        Perform logic after successful week menu creation.

        :param menu: The created week menu.
        :param request: Optional FastAPI request that triggered the operation, defaults to None.
        """
        pass

    async def on_after_update(self, updated_menu: WeekMenu, updated_menu_data: dict[str, Any],
                              request: Optional[Request] = None):
        """
        Perform logic after successful week menu update.

        :param updated_menu: Updated week menu.
        :param updated_menu_data: Dict of updated fields.
        :param request: Optional FastAPI request that triggered the operation, defaults to None.
        """
        pass

    async def on_before_delete(self, menu: WeekMenu, request: Optional[Request] = None):
        """
        Perform logic before deleting a week menu.

        :param menu: The week menu to delete.
        :param request: Optional FastAPI request that triggered the operation, defaults to None.
        """
        pass

    async def on_after_delete(self, menu: WeekMenu, request: Optional[Request] = None):
        """
        Perform logic after deleting a week menu.

        :param menu: The week menu that was deleted.
        :param request: Optional FastAPI request that triggered the operation, defaults to None.
        """
        pass

    async def _update(self, menu: WeekMenu, update_dict: dict[str, Any]) -> WeekMenu:
        validated_update_dict = {}
        for field, value in update_dict.items():
            if field == 'filename' and value != menu.filename:
                try:
                    await self.get_by_filename(value)
                    raise exceptions.WeekMenuAlreadyExists()
                except exceptions.WeekMenuNotExists:
                    validated_update_dict['filename'] = value
            else:
                validated_update_dict[field] = value
        return await self.menu_db.update(menu, validated_update_dict)


WeekMenuManagerDependency = DependencyCallable[BaseWeekMenuManager[ID]]
