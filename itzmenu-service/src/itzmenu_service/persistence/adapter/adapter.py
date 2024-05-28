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

    async def get(self, id: ID) -> WeekMenu | None:
        """Get a single week menu by id."""
        return await self.menu_model.get(id)

    async def get_by_filename(self, filename: str) -> WeekMenu | None:
        """Get a single week menu by filename."""
        return await self.menu_model.find_one({'filename': filename})

    async def get_by_timestamp(self, timestamp: int) -> WeekMenu | None:
        return await self.menu_model.find_one(self.menu_model.start_timestamp <= timestamp,
                                              self.menu_model.end_timestamp >= timestamp)

    async def get_by_timestamp_range(self, start: int, end: int) -> list[WeekMenu]:
        return await self.menu_model.find(self.menu_model.start_timestamp >= start,
                                          self.menu_model.end_timestamp <= end).to_list()

    async def create(self, create_dict: dict[str, Any]) -> WeekMenu:
        """Create a week menu."""
        user = self.menu_model(**create_dict)
        await user.create()
        return user

    async def update(self, menu: WeekMenu, update_dict: dict[str, Any]) -> WeekMenu:
        """Update a week menu."""
        for key, value in update_dict.items():
            setattr(menu, key, value)
        await menu.save()
        return menu

    async def delete(self, menu: WeekMenu) -> bool:
        """Delete a week menu."""
        result = await menu.delete()
        return result.deleted_count == 1 and result.acknowledged
