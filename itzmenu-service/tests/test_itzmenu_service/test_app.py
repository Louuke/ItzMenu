import pytest


@pytest.mark.asyncio
async def test_read_main(user_manager):
    user = await user_manager.get_by_email('fastapi@jannsen.org')
    print(user)


@pytest.mark.asyncio
async def test_read_main2(http_client):
    response = await http_client.post('/auth/login', data={"username": "fastapi@jannsen.org", "password": "password"})
    print(response.json())
