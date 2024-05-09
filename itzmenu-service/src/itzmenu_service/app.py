from contextlib import asynccontextmanager

from beanie import init_beanie
from fastapi import FastAPI, Depends

from itzmenu_service.persistence.database import User, db
from itzmenu_service.persistence.schemas import UserCreate, UserRead, UserUpdate
from itzmenu_service.manager.users import auth_backend, current_active_user, fastapi_users
from itzmenu_service.util.permissions import PermissionChecker


@asynccontextmanager
async def lifespan(fast_api: FastAPI = None):
    await init_beanie(
        database=db(),
        document_models=[
            User
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


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user),
                              _=Depends(PermissionChecker(['fastapi-users:auth']))):
    return {"message": f"Hello {user.email}!"}
