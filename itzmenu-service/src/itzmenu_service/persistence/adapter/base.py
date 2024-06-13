from typing import Generic, Any

from fastapi_users.models import ID
from fastapi_users.types import DependencyCallable

from itzmenu_service.persistence.models import WeekMenu


class BaseWeekMenuDatabase(Generic[ID]):
    """Base adapter for retrieving, creating and updating menus from a database."""

    async def get_menu_by_id(self, id: ID) -> WeekMenu | None:
        """Get a single week menu by id."""
        raise NotImplementedError()

    async def get_menu_by_checksum(self, img_checksum: str) -> WeekMenu | None:
        """Get a single week menu by image checksum."""
        raise NotImplementedError()

    async def get_menu_by_timestamp(self, timestamp: int) -> WeekMenu | None:
        """Get a single week menu by timestamp."""
        raise NotImplementedError()

    async def get_menus_by_timestamp_range(self, start: int, end: int) -> list[WeekMenu]:
        """Get a list of week menus by timestamp range."""
        raise NotImplementedError()

    async def create_menu(self, create_dict: dict[str, Any]) -> WeekMenu:
        """Create a week menu."""
        raise NotImplementedError()

    async def update_menu(self, menu: WeekMenu, update_dict: dict[str, Any]) -> WeekMenu:
        """Update a week menu."""
        raise NotImplementedError()

    async def delete_menu(self, menu: WeekMenu) -> bool:
        """Delete a week menu."""
        raise NotImplementedError()

    async def count(self) -> int:
        """Count the number of week menus."""
        raise NotImplementedError()


WeekMenuDatabaseDependency = DependencyCallable[BaseWeekMenuDatabase[ID]]
