import motor.motor_asyncio
from beanie import Document
from fastapi_users.db import BeanieBaseUser
from fastapi_users_db_beanie import BeanieUserDatabase

DATABASE_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["test"]


class User(BeanieBaseUser, Document):
    class Settings(BeanieBaseUser.Settings):
        name = "users"


async def get_user_db():
    yield BeanieUserDatabase(User)
