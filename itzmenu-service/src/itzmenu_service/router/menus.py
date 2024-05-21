from typing import Type

from fastapi import Depends, Request, APIRouter, HTTPException
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

    @router.post(
        "/",
        response_model=menu_read_schema,
        status_code=status.HTTP_201_CREATED,
        name="menus:create",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            ErrorCode.CREATE_MENU_ALREADY_EXISTS: {
                                "summary": "A week menu with this filename already exists.",
                                "value": {
                                    "detail": ErrorCode.CREATE_MENU_ALREADY_EXISTS
                                },
                            }
                        }
                    }
                },
            },
        },
    )
    async def register(request: Request, user_create: menu_create_schema,
                       user_manager: BaseWeekMenuManager[ID] = Depends(get_week_menu_manager)):
        try:
            created_user = await user_manager.create(user_create, request=request)
        except exceptions.WeekMenuAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.CREATE_MENU_ALREADY_EXISTS,
            )

        return schemas.model_validate(menu_read_schema, created_user)
    return router
