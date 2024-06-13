import logging as log
from typing import Optional
from uuid import UUID

from fastapi import Depends
from starlette.requests import Request

from itzmenu_service.manager.base import BaseWeekMenuManager
from itzmenu_service.persistence.adapter.adapter import BeanieWeekMenuDatabase
from itzmenu_service.persistence.database import get_menu_db
from itzmenu_service.persistence.models import WeekMenu


class WeekMenuManager(BaseWeekMenuManager[UUID]):

    async def on_after_create_menu(self, menu: WeekMenu, request: Optional[Request] = None):
        log.debug(f'Week menu {menu.id} has been created.')


async def get_week_menu_manager(menu_db: BeanieWeekMenuDatabase = Depends(get_menu_db)) -> WeekMenuManager:
    yield WeekMenuManager(menu_db)
