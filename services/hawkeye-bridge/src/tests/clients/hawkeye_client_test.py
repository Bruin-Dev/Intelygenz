from http.cookies import SimpleCookie
from unittest.mock import Mock, call, patch

import pytest
from aiohttp import ClientConnectionError
from application.clients.hawkeye_client import HawkeyeClient
from asynctest import CoroutineMock
from config import testconfig as config


class TestHawkeyeClient:
    def instance_test(self):
        logger = Mock()

        hawkeye_client = HawkeyeClient(logger, config)

        assert hawkeye_client._logger is logger
        assert hawkeye_client._config is config

    @pytest.mark.asyncio
    async def login_ok_test(self, hawkeye_client):
        auth_cookies = SimpleCookie()
        auth_cookies["PHPSESSID"] = "abcdefghijklmnopqrstuvwxyz123456"

        response_body = "200 - successful"
        response_status = 200

        response_mock = Mock()
        response_mock.json = CoroutineMock(return_value=response_body)
        response_mock.status = response_status
        response_mock.cookies = auth_cookies

        hawkeye_client._session.cookie_jar.update_cookies = Mock()

        with patch.object(hawkeye_client._session, "post", new=CoroutineMock(return_value=response_mock)) as mock_post:
            result = await hawkeye_client.login()

        mock_post.assert_called_once_with(
            "some.hawkeye.url/login",
            json={"username": "client_username", "password": "client_password"},
            ssl=True,
        )
        hawkeye_client._session.cookie_jar.update_cookies.assert_called_once_with(auth_cookies)

        expected_result = {
            "body": response_body,
            "status": response_status,
        }
        assert result == expected_result

    @pytest.mark.asyncio
    async def login_with_connection_error_raised_test(self, hawkeye_client):
        hawkeye_client._session.cookie_jar.update_cookies = Mock()

        with patch.object(hawkeye_client._session, "post", side_effect=ClientConnectionError) as mock_post:
            result = await hawkeye_client.login()

        mock_post.assert_called_once_with(
            "some.hawkeye.url/login",
            json={"username": "client_username", "password": "client_password"},
            ssl=True,
        )
        hawkeye_client._session.cookie_jar.update_cookies.assert_not_called()

        expected_result = {
            "body": "Error while connecting to Hawkeye API",
            "status": 500,
        }
        assert result == expected_result

    @pytest.mark.asyncio
    async def login_with_post_returning_http_401_error_test(self, hawkeye_client):
        response_status = 401

        response_mock = Mock()
        response_mock.status = response_status

        hawkeye_client._session.cookie_jar.update_cookies = Mock()

        with patch.object(hawkeye_client._session, "post", new=CoroutineMock(return_value=response_mock)) as mock_post:
            result = await hawkeye_client.login()

        mock_post.assert_called_once_with(
            "some.hawkeye.url/login",
            json={"username": "client_username", "password": "client_password"},
            ssl=True,
        )
        hawkeye_client._session.cookie_jar.update_cookies.assert_not_called()

        expected_result = {
            "body": "Username doesn't exist or password is incorrect",
            "status": response_status,
        }
        assert result == expected_result

    @pytest.mark.asyncio
    async def login_with_post_returning_http_5xx_error_test(self, hawkeye_client):
        response_status = 502

        response_mock = Mock()
        response_mock.status = response_status

        hawkeye_client._session.cookie_jar.update_cookies = Mock()

        with patch.object(hawkeye_client._session, "post", new=CoroutineMock(return_value=response_mock)) as mock_post:
            result = await hawkeye_client.login()

        mock_post.assert_called_once_with(
            "some.hawkeye.url/login",
            json={"username": "client_username", "password": "client_password"},
            ssl=True,
        )
        hawkeye_client._session.cookie_jar.update_cookies.assert_not_called()

        expected_result = {
            "body": "Got internal error from Hawkeye",
            "status": 500,
        }
        assert result == expected_result

    @pytest.mark.asyncio
    async def get_probes_ok_test(self, hawkeye_client, get_probes_down, default_call_without_params):
        filters = default_call_without_params
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_probes_down)
        response_mock.status = 200
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_probes(filters)
            mock_get.assert_called_once()
            assert result["body"] == get_probes_down
            assert result["status"] == 200
        mock_get.assert_called_once_with(
            "some.hawkeye.url/probes",
            params=filters,
            ssl=True,
        )

    @pytest.mark.asyncio
    async def get_probes_retries_ok_test(self, hawkeye_client, get_probes_down):
        topic = "some.hawkeye.url/probes"
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 401
        hawkeye_client.login = CoroutineMock()
        response_mock_2 = CoroutineMock()
        response_mock_2.json = CoroutineMock(return_value=get_probes_down)
        response_mock_2.status = 200
        with patch.object(
            hawkeye_client._session, "get", new=CoroutineMock(side_effect=[response_mock, response_mock_2])
        ) as mock_get:
            result = await hawkeye_client.get_probes(filters)
            mock_get.assert_has_calls([call(topic, params=filters, ssl=True), call(topic, params=filters, ssl=True)])
            assert result["body"] == get_probes_down
            assert result["status"] == 200

    @pytest.mark.asyncio
    async def get_probes_401_test(self, hawkeye_client):
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 401
        hawkeye_client.login = CoroutineMock()
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_probes(filters)
            assert result["body"] == "Got 401 from Hawkeye"
            assert result["status"] == 401

    @pytest.mark.asyncio
    async def get_probes_retries_ko_test(self, hawkeye_client):
        topic = "some.hawkeye.url/probes"
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 401
        hawkeye_client.login = CoroutineMock()
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_probes(filters)
            mock_get.assert_has_calls(
                [
                    call(topic, params=filters, ssl=True),
                    call(topic, params=filters, ssl=True),
                    call(topic, params=filters, ssl=True),
                    call(topic, params=filters, ssl=True),
                    call(topic, params=filters, ssl=True),
                    call(topic, params=filters, ssl=True),
                ]
            )
            assert result["body"] == "Got 401 from Hawkeye"
            assert result["status"] == 401

    @pytest.mark.asyncio
    async def get_probes_500_test(self, hawkeye_client):
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 500
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_probes(filters)
            mock_get.assert_called_once()
            assert result["body"] == "Got internal error from Hawkeye"
            assert result["status"] == 500

    @pytest.mark.asyncio
    async def get_probes_exception_test(self, hawkeye_client):
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 500
        with patch.object(hawkeye_client._session, "get", side_effect=Exception) as mock_get:
            result = await hawkeye_client.get_probes(filters)
            mock_get.assert_called_once()
            assert result["body"] == "Error while connecting to Hawkeye API"
            assert result["status"] == 500

    @pytest.mark.asyncio
    async def get_test_results_ok_test(self, hawkeye_client, get_test_result):
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_test_result)
        response_mock.status = 200
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_tests_results(filters)
            mock_get.assert_called_once()
            assert result["body"] == get_test_result
            assert result["status"] == 200
        mock_get.assert_called_once_with(
            "some.hawkeye.url/testsresults",
            params=filters,
            ssl=True,
        )

    @pytest.mark.asyncio
    async def get_test_result_retries_ok_test(self, hawkeye_client, get_test_result):
        topic = "some.hawkeye.url/testsresults"
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 401
        hawkeye_client.login = CoroutineMock()
        response_mock_2 = CoroutineMock()
        response_mock_2.json = CoroutineMock(return_value=get_test_result)
        response_mock_2.status = 200
        with patch.object(
            hawkeye_client._session, "get", new=CoroutineMock(side_effect=[response_mock, response_mock_2])
        ) as mock_get:
            result = await hawkeye_client.get_tests_results(filters)
            mock_get.assert_has_calls([call(topic, params=filters, ssl=True), call(topic, params=filters, ssl=True)])
            assert result["body"] == get_test_result
            assert result["status"] == 200

    @pytest.mark.asyncio
    async def get_test_result_401_test(self, hawkeye_client):
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 401
        hawkeye_client.login = CoroutineMock()
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_tests_results(filters)
            assert result["body"] == "Got 401 from Hawkeye"
            assert result["status"] == 401

    @pytest.mark.asyncio
    async def get_test_result_retries_ko_test(self, hawkeye_client):
        topic = "some.hawkeye.url/testsresults"
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 401
        hawkeye_client.login = CoroutineMock()
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_tests_results(filters)
            mock_get.assert_has_calls(
                [
                    call(topic, params=filters, ssl=True),
                    call(topic, params=filters, ssl=True),
                    call(topic, params=filters, ssl=True),
                    call(topic, params=filters, ssl=True),
                    call(topic, params=filters, ssl=True),
                    call(topic, params=filters, ssl=True),
                ]
            )
            assert result["body"] == "Got 401 from Hawkeye"
            assert result["status"] == 401

    @pytest.mark.asyncio
    async def get_test_result_500_test(self, hawkeye_client):
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 500
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_tests_results(filters)
            mock_get.assert_called_once()
            assert result["body"] == "Got internal error from Hawkeye"
            assert result["status"] == 500

    @pytest.mark.asyncio
    async def get_test_result_400_test(self, hawkeye_client):
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 400
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_tests_results(filters)
            mock_get.assert_called_once()
            assert result["body"] == "Parameters or body were in an incorrect format"
            assert result["status"] == 400

    @pytest.mark.asyncio
    async def get_test_result_exception_test(self, hawkeye_client):
        filters = {"request_id": "1234", "body": {}}
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 500
        with patch.object(hawkeye_client._session, "get", side_effect=Exception) as mock_get:
            result = await hawkeye_client.get_tests_results(filters)
            mock_get.assert_called_once()
            assert result["body"] == "Error while connecting to Hawkeye API"
            assert result["status"] == 500

    @pytest.mark.asyncio
    async def get_test_results_details_ok_test(self, hawkeye_client, get_test_result_details):
        id_test = "12345"
        topic = f"some.hawkeye.url/testsresults/{id_test}"
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock(return_value=get_test_result_details)
        response_mock.status = 200
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_test_result_details(id_test)
            mock_get.assert_called_once()
            assert result["body"] == get_test_result_details
            assert result["status"] == 200
        mock_get.assert_called_once_with(
            topic,
            ssl=True,
        )

    @pytest.mark.asyncio
    async def get_test_result_retries_details_ok_test(self, hawkeye_client, get_test_result):
        id_test = "12345"
        topic = f"some.hawkeye.url/testsresults/{id_test}"
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 401
        hawkeye_client.login = CoroutineMock()
        response_mock_2 = CoroutineMock()
        response_mock_2.json = CoroutineMock(return_value=get_test_result)
        response_mock_2.status = 200
        with patch.object(
            hawkeye_client._session, "get", new=CoroutineMock(side_effect=[response_mock, response_mock_2])
        ) as mock_get:
            result = await hawkeye_client.get_test_result_details(id_test)
            mock_get.assert_has_calls([call(topic, ssl=True), call(topic, ssl=True)])
            assert result["body"] == get_test_result
            assert result["status"] == 200

    @pytest.mark.asyncio
    async def get_test_result_details_401_test(self, hawkeye_client):
        id_test = "12345"
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 401
        hawkeye_client.login = CoroutineMock()
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_test_result_details(id_test)
            assert result["body"] == "Got 401 from Hawkeye"
            assert result["status"] == 401

    @pytest.mark.asyncio
    async def get_test_result_retries_details_ko_test(self, hawkeye_client):
        id_test = "12345"
        topic = f"some.hawkeye.url/testsresults/{id_test}"
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 401
        hawkeye_client.login = CoroutineMock()
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_test_result_details(id_test)
            mock_get.assert_has_calls(
                [
                    call(topic, ssl=True),
                    call(topic, ssl=True),
                    call(topic, ssl=True),
                    call(topic, ssl=True),
                    call(topic, ssl=True),
                    call(topic, ssl=True),
                ]
            )
            assert result["body"] == "Got 401 from Hawkeye"
            assert result["status"] == 401

    @pytest.mark.asyncio
    async def get_test_result_details_500_test(self, hawkeye_client):
        id_test = "12345"
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 500
        with patch.object(hawkeye_client._session, "get", new=CoroutineMock(return_value=response_mock)) as mock_get:
            result = await hawkeye_client.get_test_result_details(id_test)
            mock_get.assert_called_once()
            assert result["body"] == "Got internal error from Hawkeye"
            assert result["status"] == 500

    @pytest.mark.asyncio
    async def get_test_result_details_exception_test(self, hawkeye_client):
        id_test = "12345"
        response_mock = CoroutineMock()
        response_mock.json = CoroutineMock()
        response_mock.status = 500
        with patch.object(hawkeye_client._session, "get", side_effect=Exception) as mock_get:
            result = await hawkeye_client.get_test_result_details(id_test)
            mock_get.assert_called_once()
            assert result["body"] == "Error while connecting to Hawkeye API"
            assert result["status"] == 500
