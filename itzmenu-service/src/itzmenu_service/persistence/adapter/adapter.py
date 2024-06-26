from typing import Type, Any, Optional
from uuid import UUID

from fastapi_users.models import ID

from itzmenu_service.persistence.adapter.base import BaseWeekMenuDatabase
from itzmenu_service.persistence.models import WeekMenu


class BeanieWeekMenuDatabase(BaseWeekMenuDatabase[UUID]):
    """
    Database adapter for Beanie.

    :param menu_model: Beanie week menu model.
    """

    def __init__(self, menu_model: Type[WeekMenu]):
        self.menu_model = menu_model

    async def get_menu_by_id(self, id: ID) -> WeekMenu | None:
        """Get a single week menu by id."""
        return await self.menu_model.get(id)

    async def get_menu_by_checksum(self, img_checksum: str) -> WeekMenu | None:
        """Get a single week menu by image checksum."""
        return await self.menu_model.find_one({'img_checksum': img_checksum})

    async def get_menu_by_timestamp(self, timestamp: int) -> WeekMenu | None:
        return await self.menu_model.find_one(self.menu_model.start_timestamp <= timestamp,
                                              self.menu_model.end_timestamp >= timestamp)

    async def get_menus_by_timestamp_range(self, start: int, end: int) -> list[WeekMenu]:
        return await self.menu_model.find(self.menu_model.start_timestamp >= start,
                                          self.menu_model.end_timestamp <= end).to_list()

    async def create_menu(self, create_dict: dict[str, Any]) -> WeekMenu:
        """Create a week menu."""
        menu = self.menu_model(**create_dict)
        await menu.create()
        return menu

    async def update_menu(self, menu: WeekMenu, update_dict: dict[str, Any]) -> WeekMenu:
        """Update a week menu."""
        for key, value in update_dict.items():
            setattr(menu, key, value)
        await menu.save()
        return menu

    async def delete_menu(self, menu: WeekMenu) -> bool:
        """Delete a week menu."""
        result = await menu.delete()
        return result.deleted_count == 1 and result.acknowledged

    async def count(self) -> int:
        """Count the number of week menus."""
        return await self.menu_model.count()
