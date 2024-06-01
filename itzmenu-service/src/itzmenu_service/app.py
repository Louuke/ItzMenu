from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI, Depends

from itzmenu_service.manager.menus import get_week_menu_manager
from itzmenu_service.persistence.database import db
from itzmenu_service.persistence.models import User, WeekMenu
from itzmenu_api.persistence.schemas import UserCreate, UserRead, UserUpdate, WeekMenuRead, WeekMenuCreate
from itzmenu_service.manager.users import auth_backend, fastapi_users
from itzmenu_service.router.menus import get_menus_router
from itzmenu_service.authentication.permissions import PermissionChecker


@asynccontextmanager
async def lifespan(fast_api: FastAPI = None):
    await init_beanie(
        database=db(),
        document_models=[
            User,
            WeekMenu
        ],
    )
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)
app.include_router(
    get_menus_router(get_week_menu_manager, WeekMenuRead, WeekMenuCreate),
    prefix="/menus",
    tags=["menus"],
)


@app.get("/authenticated-route")
async def authenticated_route(_=Depends(PermissionChecker(['fastapi-users:auth']))):
    return {"message": f"Hello!"}
