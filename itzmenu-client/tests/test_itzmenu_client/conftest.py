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
         'created_at': 30, 'filename': 'test_menu1.jpg'},
        {'id': '835849f9-52e9-4479-8cc3-63ac96e75326', 'start_timestamp': 41, 'end_timestamp': 50,
         'created_at': 41, 'filename': 'test_menu2.jpg'},
    ]


@pytest.fixture
def httpserver(make_httpserver, user: str, password: str, user_access_token: str):
    server: HTTPServer = make_httpserver
    data = f'username={urllib.parse.quote(user)}&password={password}'
    resp = {'access_token': user_access_token, 'token_type': 'bearer'}
    server.expect_request('/auth/login', method='POST', data=data).respond_with_json(resp)
    yield server
    server.clear()
