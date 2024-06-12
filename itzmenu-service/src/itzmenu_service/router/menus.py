import time
import re
from typing import Type

from fastapi import Depends, Request, APIRouter, HTTPException, Path
from fastapi_users import schemas
from fastapi_users.models import ID
from fastapi_users.router.common import ErrorModel
from starlette import status

from itzmenu_api.persistence.schemas import WeekMenuRead, WeekMenuUpdate, WeekMenuCreate
from itzmenu_service.authentication.permissions import PermissionChecker
from itzmenu_service.manager import exceptions
from itzmenu_service.manager.base import WeekMenuManagerDependency, BaseWeekMenuManager
from itzmenu_service.persistence.models import WeekMenu
from itzmenu_service.router.common import ErrorCode


def get_menus_router(get_week_menu_manager: WeekMenuManagerDependency[ID],
                     menu_read_schema: Type[WeekMenuRead],
                     menu_create_schema: Type[WeekMenuCreate]) -> APIRouter:
    """Generate a router with the week menu route."""
    router = APIRouter()

    @router.post('', response_model=menu_read_schema, status_code=status.HTTP_201_CREATED,
                 name='menus:create_menu',
                 responses={
                     status.HTTP_400_BAD_REQUEST: {
                         'mode': ErrorModel,
                         'content': {
                             'application/json': {
                                 'examples': {
                                     ErrorCode.MENU_WITH_CHECKSUM_ALREADY_EXISTS: {
                                         'summary': 'A menu with the given checksum already exists.',
                                         'value': {
                                             'detail': ErrorCode.MENU_WITH_CHECKSUM_ALREADY_EXISTS
                                         },
                                     }
                                 }
                             }
                         },
                     },
                 })
    async def create_menu(request: Request, user_create: menu_create_schema,
                          menu_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager),
                          _=Depends(PermissionChecker(['menus:create_menu']))):
        try:
            created_user = await menu_manager.create(user_create, request=request)
        except exceptions.WeekMenuAlreadyExists as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=ErrorCode.MENU_WITH_CHECKSUM_ALREADY_EXISTS) from e
        return schemas.model_validate(menu_read_schema, created_user)

    @router.get('/menu/{id_or_checksum}', response_model=menu_read_schema, name='menus:get_menu_by_id')
    async def get_menu_by_id(id_or_checksum: str, include_image: bool = False,
                             menu_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager)):
        return await __get_menu_by(menu_manager, id_or_checksum=id_or_checksum, include_image=include_image)

    @router.get('', response_model=list[menu_read_schema], name='menus:get_menu_by_timestamp_range')
    async def get_menu_by_timestamp_range(menu_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager),
                                          start: int = 0, end: int = 9999999999, include_image: bool = False):
        return await menu_manager.get_by_timestamp_range(start, end, include_image)

    @router.get('/menu', response_model=menu_read_schema, name='menus:get_menu_by_timestamp')
    async def get_menu_by_timestamp(menu_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager),
                                    timestamp: int = int(time.time()), include_image: bool = False):
        return await __get_menu_by(menu_manager, timestamp=timestamp, include_image=include_image)

    @router.patch('/menu/{id_or_checksum}', response_model=menu_read_schema, name='menus:update_menu')
    async def update_menu(request: Request, id_or_checksum: str, user_update: WeekMenuUpdate,
                          menu_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager),
                          _=Depends(PermissionChecker(['menus:update_menu']))):
        try:
            current_menu = await __get_menu_by(menu_manager, id_or_checksum=id_or_checksum, include_image=True)
            menu = await menu_manager.update(user_update, current_menu, request=request)
            return schemas.model_validate(menu_read_schema, menu)
        except exceptions.WeekMenuAlreadyExists as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=ErrorCode.MENU_WITH_CHECKSUM_ALREADY_EXISTS) from e

    @router.delete('/menu/{id_or_checksum}', status_code=status.HTTP_204_NO_CONTENT, name='menus:delete_menu')
    async def delete_menu(id_or_checksum: str, menu_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager),
                          _=Depends(PermissionChecker(['menus:delete_menu']))):
        menu = await __get_menu_by(menu_manager, id_or_checksum=id_or_checksum, include_image=True)
        await menu_manager.delete(menu)

    async def __get_menu_by(menu_manager: BaseWeekMenuManager[ID], id_or_checksum: str | None = None,
                            include_image: bool = False, timestamp: int | None = None) -> WeekMenu:
        try:
            if timestamp is not None:
                return await menu_manager.get_by_timestamp(timestamp, include_image)
            elif re.search(r'^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$', id_or_checksum):
                return await menu_manager.get_by_id(id_or_checksum, include_image)
            else:
                return await menu_manager.get_by_image(id_or_checksum, include_image)
        except exceptions.WeekMenuNotExists as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=ErrorCode.MENU_NOT_FOUND) from e

    async def __get_image_by(menu_manager: BaseWeekMenuManager[ID], id_or_checksum: str):
        try:
            if re.search(r'^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$', id_or_checksum):
                return await menu_manager.get_image_by_id(id_or_checksum)
            else:
                return await menu_manager.get_image_by_checksum(id_or_checksum)
        except exceptions.WeekMenuNotExists as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=ErrorCode.MENU_NOT_FOUND) from e

    return router
