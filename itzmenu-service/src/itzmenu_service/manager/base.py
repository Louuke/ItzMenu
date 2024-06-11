from typing import Generic, Optional, Any

from fastapi import Request
from fastapi_users.models import ID
from fastapi_users.types import DependencyCallable

from itzmenu_api.persistence.schemas import WeekMenuCreate, WeekMenuUpdate
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

    async def get_by_id(self, id: ID) -> WeekMenu:
        """
        Get a week menu by id.

        :param id: Id. of the week menu to retrieve.
        :raises WeekMenuNotExists: The week menu does not exist.
        :return: A week menu.
        """
        if (menu := await self.menu_db.get_by_id(id)) is None:
            raise exceptions.WeekMenuNotExists()
        return menu

    async def get_by_image(self, img_checksum: str) -> WeekMenu:
        """
        Get a week menu by image checksum.

        :param img_checksum: Image checksum of the week menu to retrieve.
        :return: A week menu.
        """
        if (menu := await self.menu_db.get_by_image(img_checksum)) is None:
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

    async def get_by_timestamp_range(self, start: int, end: int) -> list[WeekMenu]:
        """
        Get a list of week menus by timestamp range.

        :param start: Start of the timestamp range.
        :param end: End of the timestamp range.
        :return: A list of week menus.
        """
        return await self.menu_db.get_by_timestamp_range(start, end)

    async def create(self, menu_create: WeekMenuCreate, request: Optional[Request] = None) -> WeekMenu:
        """
        Create a week menu in database.

        Triggers the on_after_new_menu handler on success.

        :param menu_create: The CreateWeekMenu model to create.
        :param request: Optional FastAPI request that triggered the operation, defaults to None.
        :raises WeekMenuAlreadyExists: A user already exists with the same e-mail.
        :return: A new week menu.
        """
        existing_menu = await self.menu_db.get_by_image(menu_create.img_checksum)
        if existing_menu is not None:
            raise exceptions.WeekMenuAlreadyExists()

        menu_dict = menu_create.create_update_dict()
        created_menu = await self.menu_db.create(menu_dict)
        await self.on_after_create(created_menu, request)
        return created_menu

    async def update(self, menu_update: WeekMenuUpdate, menu: WeekMenu, request: Optional[Request] = None) -> WeekMenu:
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

    async def delete(self, menu: WeekMenu, request: Optional[Request] = None) -> bool:
        """
        Delete a user.

        :param menu: The week menu to delete.
        :param request: Optional FastAPI request that triggered the operation, defaults to None.
        """
        await self.on_before_delete(menu, request)
        result = await self.menu_db.delete(menu)
        await self.on_after_delete(menu, request)
        return result

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
            if field == 'img_checksum' and value != menu.img_checksum:
                try:
                    await self.get_by_image(value)
                    raise exceptions.WeekMenuAlreadyExists()
                except exceptions.WeekMenuNotExists:
                    validated_update_dict['img_checksum'] = value
            else:
                validated_update_dict[field] = value
        return await self.menu_db.update(menu, validated_update_dict)

    @staticmethod
    def _get(get_func: callable, include_images: bool):
        """
        Get a week menu by id, image checksum or timestamp.
        :param get_func: The function to call to retrieve the week menu.
        :param include_images: Whether to include images in the response.
        :return: The week menu.
        """
        def exclude_img(menu: WeekMenu) -> WeekMenu:
            return WeekMenu(**menu.dict(exclude={'img'})) if not include_images else menu

        if (result := get_func()) is None:
            raise exceptions.WeekMenuNotExists()
        elif type(result) is list:
            return [exclude_img(menu_item) for menu_item in result]
        return exclude_img(result)


WeekMenuManagerDependency = DependencyCallable[BaseWeekMenuManager[ID]]
