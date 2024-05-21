import time
from typing import Type, Optional
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
                          user_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager)):
        try:
            created_user = await user_manager.create(user_create, request=request)
        except exceptions.WeekMenuAlreadyExists as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=ErrorCode.CREATE_MENU_ALREADY_EXISTS) from e
        return schemas.model_validate(menu_read_schema, created_user)

    @router.get('/{menu_id}', response_model=menu_read_schema, name='menus:get_menu')
    async def get_menu(menu_id: UUID = Path(...),
                       user_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager)):
        try:
            menu = await user_manager.get(menu_id)
            return menu
        except exceptions.WeekMenuNotExists as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=ErrorCode.GET_MENU_NOT_FOUND) from e

    @router.get('/', response_model=menu_read_schema, name='menus:filter_menu')
    async def filter_menu(user_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager),
                          timestamp: Optional[int] = time.time()):
        try:
            menu = await user_manager.get_by_timestamp(timestamp)
            return menu
        except exceptions.WeekMenuNotExists as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=ErrorCode.GET_MENU_NOT_FOUND) from e

    return router
