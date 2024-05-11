import time
import uuid
from typing import Optional, Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from itzmenu_api.persistence.enums import DietType, WeekDay


def model_dump(model: BaseModel, *args, **kwargs) -> dict[str, Any]:
    return model.model_dump(*args, **kwargs)


class UpdateDictModel(BaseModel):

    def __init__(self, exclude: set[str] = None, exclude_unset: bool = True):
        super().__init__()
        self.__exclude_superuser = {'id'}
        self.__exclude = self.__exclude_superuser.union(exclude) if exclude is not None else self.__exclude_superuser
        self.__exclude_unset = exclude_unset

    def create_update_dict(self) -> dict[str, Any]:
        return model_dump(self, exclude_unset=self.__exclude_unset, exclude=self.__exclude)

    def create_update_dict_superuser(self):
        return model_dump(self, exclude_unset=True, exclude=self.__exclude_superuser)


class UserUpdateDictModel(UpdateDictModel):
    def __init__(self):
        super().__init__(exclude={'is_superuser', 'is_active', 'is_verified', 'oauth_accounts', 'permissions'})


class UserRead(UserUpdateDictModel):
    id: uuid.UUID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False
    permissions: set[str] = Field(default={})

    model_config = ConfigDict(from_attributes=True)


class UserCreate(UserUpdateDictModel):
    email: EmailStr
    password: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False
    is_verified: Optional[bool] = False
    permissions: Optional[set[str]] = Field(default={})


class UserUpdate(UserUpdateDictModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_verified: Optional[bool] = None
    permissions: Optional[set[str]] = []
    permissions: Optional[set[str]] = None
