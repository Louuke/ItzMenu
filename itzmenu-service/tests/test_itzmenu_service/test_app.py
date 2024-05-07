import asyncio
import contextlib

import itzmenu_service.app as app
from itzmenu_service.manager.users import get_user_manager
from itzmenu_service.persistence.database import get_user_db


def test_register_router():
    asyncio.run(find_user('test@test.com'))


get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def find_user(email: str):
    async with app.lifespan():
        async with get_user_db_context() as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                user = await user_manager.get_by_email(email)
                print(user)
                return user
