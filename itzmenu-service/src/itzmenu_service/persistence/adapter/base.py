from typing import Optional, Generic, Any

from fastapi_users.models import ID
from fastapi_users.types import DependencyCallable

from itzmenu_service.persistence.models import WeekMenu


class BaseWeekMenuDatabase(Generic[ID]):
    """Base adapter for retrieving, creating and updating menus from a database."""

    async def get(self, id: ID) -> Optional[WeekMenu]:
        """Get a single week menu by id."""
        raise NotImplementedError()

    async def get_by_filename(self, filename: str) -> Optional[WeekMenu]:
        """Get a single week menu by filename."""
        raise NotImplementedError()

    async def create(self, create_dict: dict[str, Any]) -> WeekMenu:
        """Create a week menu."""
        raise NotImplementedError()

    async def update(self, menu: WeekMenu, update_dict: dict[str, Any]) -> WeekMenu:
        """Update a week menu."""
        raise NotImplementedError()

    async def delete(self, menu: WeekMenu) -> None:
        """Delete a week menu."""
        raise NotImplementedError()


WeekMenuDatabaseDependency = DependencyCallable[BaseWeekMenuDatabase[ID]]