import time
import re
from typing import Type
from uuid import UUID

from fastapi import Depends, Request, APIRouter, HTTPException, Path
from fastapi_users import schemas
from fastapi_users.models import ID
from fastapi_users.router.common import ErrorModel
from starlette import status

from itzmenu_api.persistence.schemas import WeekMenuRead, WeekMenuCreate
from itzmenu_service.manager import exceptions
from itzmenu_service.manager.base import WeekMenuManagerDependency, BaseWeekMenuManager
from itzmenu_service.router.common import ErrorCode


def get_menus_router(get_week_menu_manager: WeekMenuManagerDependency[ID],
                     menu_read_schema: Type[WeekMenuRead],
                     menu_create_schema: Type[WeekMenuCreate]) -> APIRouter:
    """Generate a router with the week menu route."""
    router = APIRouter()

    @router.post('/', response_model=menu_read_schema, status_code=status.HTTP_201_CREATED,
                 name='menus:create_menu',
                 responses={
                     status.HTTP_400_BAD_REQUEST: {
                         'mode': ErrorModel,
                         'content': {
                             'application/json': {
                                 'examples': {
                                     ErrorCode.CREATE_MENU_ALREADY_EXISTS: {
                                         'summary': 'A week menu with this filename already exists.',
                                         'value': {
                                             'detail': ErrorCode.CREATE_MENU_ALREADY_EXISTS
                                         },
                                     }
                                 }
                             }
                         },
                     },
                 })
    async def create_menu(request: Request, user_create: menu_create_schema,
                          menu_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager)):
        try:
            created_user = await menu_manager.create(user_create, request=request)
        except exceptions.WeekMenuAlreadyExists as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=ErrorCode.CREATE_MENU_ALREADY_EXISTS) from e
        return schemas.model_validate(menu_read_schema, created_user)

    @router.get('/{id_or_filename}', response_model=menu_read_schema, name='menus:get_menu_by_id')
    async def get_menu_by_id(id_or_filename: UUID | str = Path(...),
                             menu_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager)):
        try:
            if re.search(r'^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$', id_or_filename):
                return await menu_manager.get(id_or_filename)
            else:
                return await menu_manager.get_by_filename(id_or_filename)
        except exceptions.WeekMenuNotExists as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=ErrorCode.GET_MENU_NOT_FOUND) from e

    @router.get('/', response_model=list[menu_read_schema], name='menus:get_menu_by_timestamp_range')
    async def get_menu_by_timestamp_range(menu_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager),
                                          start: int = 0, end: int = 9999999999):
        return await menu_manager.get_by_timestamp_range(start, end)

    @router.get('/week/', response_model=menu_read_schema, name='menus:get_menu_by_timestamp')
    async def get_menu_by_timestamp(menu_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager),
                                    timestamp: int = int(time.time())):
        try:
            return await menu_manager.get_by_timestamp(timestamp)
        except exceptions.WeekMenuNotExists as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=ErrorCode.GET_MENU_NOT_FOUND) from e

    return router
