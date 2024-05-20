from typing import Type, Any
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

    async def get(self, id: ID) -> WeekMenu:
        """Get a single week menu by id."""
        return await self.menu_model.get(id)

    async def get_by_filename(self, filename: str) -> WeekMenu:
        """Get a single week menu by filename."""
        return await self.menu_model.find_one({'filename': filename})

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

    async def delete(self, menu: WeekMenu) -> None:
        """Delete a week menu."""
        await menu.delete()
