import uuid
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict, EmailStr


def model_dump(model: BaseModel, *args, **kwargs) -> dict[str, Any]:
    return model.model_dump(*args, **kwargs)


class UserUpdateDictModel(BaseModel):
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

    def create_update_dict_superuser(self):
        return model_dump(self, exclude_unset=True, exclude={'id'})


class UserRead(UserUpdateDictModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    permissions: set[str] = []

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserUpdateDictModel):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    permissions: Optional[set[str]] = []


class UserUpdate(UserUpdateDictModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    permissions: Optional[set[str]] = []
