from typing import Optional, Any

from beanie import PydanticObjectId
from fastapi_users import schemas
from fastapi_users.schemas import model_dump
from pydantic import BaseModel


class OverrideUpdateDictModel(BaseModel):
    def create_update_dict(self) -> dict[str, Any]:
        return model_dump(
            self,
            exclude_unset=True,
            exclude={
                'id',
                'is_superuser',
                'is_active',
                'is_verified',
                'oauth_accounts',
                'permissions'
            },
        )


class UserRead(OverrideUpdateDictModel, schemas.BaseUser[PydanticObjectId]):
    permissions: set[str] = []


class UserCreate(OverrideUpdateDictModel, schemas.BaseUserCreate):
    permissions: Optional[set[str]] = []


class UserUpdate(OverrideUpdateDictModel, schemas.BaseUserUpdate):
    permissions: Optional[set[str]] = []
