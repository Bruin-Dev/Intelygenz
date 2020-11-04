from http.cookies import SimpleCookie
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from aiohttp import ClientConnectionError

from asynctest import CoroutineMock

from application.clients.hawkeye_client import HawkeyeClient
from config import testconfig as config


class TestHawkeyeClient:
    def instance_test(self):
        logger = Mock()

        hawkeye_client = HawkeyeClient(logger, config)

        assert hawkeye_client._logger is logger
        assert hawkeye_client._config is config

    @pytest.mark.asyncio
    async def login_ok_test(self):
        auth_cookies = SimpleCookie()
        auth_cookies['PHPSESSID'] = 'abcdefghijklmnopqrstuvwxyz123456'

        response_body = '200 - successful'
        response_status = 200

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=response_body)
        response_mock.status = response_status
        response_mock.cookies = auth_cookies

        logger = Mock()

        hawkeye_client = HawkeyeClient(logger, config)
        hawkeye_client._session.cookie_jar.update_cookies = Mock()

        with patch.object(hawkeye_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            result = await hawkeye_client.login()

        mock_post.assert_called_once_with(
            'some.hawkeye.url/login',
            json={'username': 'client_username', 'password': 'client_password'},
            ssl=True,
        )
        hawkeye_client._session.cookie_jar.update_cookies.assert_called_once_with(auth_cookies)

        expected_result = {
            'body': response_body,
            'status': response_status,
        }
        assert result == expected_result

    @pytest.mark.asyncio
    async def login_with_connection_error_raised_test(self):
        logger = Mock()

        hawkeye_client = HawkeyeClient(logger, config)
        hawkeye_client._session.cookie_jar.update_cookies = Mock()

        with patch.object(hawkeye_client._session, 'post', side_effect=ClientConnectionError) as mock_post:
            result = await hawkeye_client.login()

        mock_post.assert_called_once_with(
            'some.hawkeye.url/login',
            json={'username': 'client_username', 'password': 'client_password'},
            ssl=True,
        )
        hawkeye_client._session.cookie_jar.update_cookies.assert_not_called()

        expected_result = {
            'body': 'Error while connecting to Hawkeye API',
            'status': 500,
        }
        assert result == expected_result

    @pytest.mark.asyncio
    async def login_with_post_returning_http_401_error_test(self):
        response_status = 401

        response_mock = Mock()
        response_mock.status = response_status

        logger = Mock()

        hawkeye_client = HawkeyeClient(logger, config)
        hawkeye_client._session.cookie_jar.update_cookies = Mock()

        with patch.object(hawkeye_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            result = await hawkeye_client.login()

        mock_post.assert_called_once_with(
            'some.hawkeye.url/login',
            json={'username': 'client_username', 'password': 'client_password'},
            ssl=True,
        )
        hawkeye_client._session.cookie_jar.update_cookies.assert_not_called()

        expected_result = {
            'body': "Username doesn't exist or password is incorrect",
            'status': response_status,
        }
        assert result == expected_result

    @pytest.mark.asyncio
    async def login_with_post_returning_http_5xx_error_test(self):
        response_status = 502

        response_mock = Mock()
        response_mock.status = response_status

        logger = Mock()

        hawkeye_client = HawkeyeClient(logger, config)
        hawkeye_client._session.cookie_jar.update_cookies = Mock()

        with patch.object(hawkeye_client._session, 'post', new=CoroutineMock(return_value=response_mock)) as mock_post:
            result = await hawkeye_client.login()

        mock_post.assert_called_once_with(
            'some.hawkeye.url/login',
            json={'username': 'client_username', 'password': 'client_password'},
            ssl=True,
        )
        hawkeye_client._session.cookie_jar.update_cookies.assert_not_called()

        expected_result = {
            'body': "Got internal error from Hawkeye",
            'status': 500,
        }
        assert result == expected_result
