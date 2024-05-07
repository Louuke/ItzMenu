import motor.motor_asyncio
from itzmenu_service.persistence.models import User
from fastapi_users_db_beanie import BeanieUserDatabase


DATABASE_URL = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(
    DATABASE_URL, uuidRepresentation="standard"
)
db = client["test"]


async def get_user_db():
    yield BeanieUserDatabase(User)
