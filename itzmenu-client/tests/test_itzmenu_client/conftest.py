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
def week_menus() -> list[dict[str, str]]:
    return [
        {'id': '835849f9-52e9-4479-8cc3-63ac96e75325', 'start_timestamp': 30, 'end_timestamp': 40,
         'created_at': 30, 'img_checksum': '03043c5abd66e979d1ab97f3be8a1bc2d8ba993b3374c774f93b698e1c8376b6'},
        {'id': '835849f9-52e9-4479-8cc3-63ac96e75326', 'start_timestamp': 41, 'end_timestamp': 50,
         'created_at': 41, 'img_checksum': 'f396316a7250d1c1d38e7c606a37ae6366db2e991750f4bfab5deee4166d1dc8'},
    ]


@pytest.fixture
def httpserver(make_httpserver, user: str, password: str, user_access_token: str):
    server: HTTPServer = make_httpserver
    data = f'username={urllib.parse.quote(user)}&password={password}'
    resp = {'access_token': user_access_token, 'token_type': 'bearer'}
    server.expect_request('/auth/login', method='POST', data=data).respond_with_json(resp)
    yield server
    server.clear()
