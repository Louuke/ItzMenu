import urllib.parse

import pytest
from pytest_httpserver import HTTPServer


@pytest.fixture
def user():
    return 'user@example.org'


@pytest.fixture
def password():
    return 'paSSw0rd'


@pytest.fixture
def user_access_token():
    return 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiaWF0IjoxNjI4MzQwNzI3LCJleHAiOjE2MjgzNDA3Mjd9'


@pytest.fixture
def headers(user_access_token: str):
    return {'Authorization': f'Bearer {user_access_token}'}


@pytest.fixture
def httpserver(make_httpserver, user: str, password: str, user_access_token: str):
    server: HTTPServer = make_httpserver
    data = f'username={urllib.parse.quote(user)}&password={password}'
    resp = {'access_token': user_access_token, 'token_type': 'bearer'}
    server.expect_request('/auth/login', method='POST', data=data).respond_with_json(resp)
    yield server
    server.clear()
