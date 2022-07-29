import asyncio
from unittest.mock import AsyncMock, Mock, patch

from dataclasses import asdict
from framework.nats.client import Client
from framework.nats.client import Client_ as RealClient
from framework.nats.exceptions import BadSubjectError, NatsConnectionError, ResponseTimeoutError
from framework.nats.models import Connection, Publish, Request, Subscription
from framework.nats.temp_payload_storage import TempPayloadStorage
from nats import errors
from nats.aio.client import DEFAULT_MAX_PAYLOAD_SIZE
from nats.aio.msg import Msg as NatsMessage
from pytest import fixture, raises


@fixture(scope="function")
def dummy_temp_payload_storage():
    return Mock(spec_set=TempPayloadStorage)


@fixture(scope="function")
def client(dummy_temp_payload_storage):
    return Client(temp_payload_storage=dummy_temp_payload_storage)


@fixture(scope="function")
def connection_model():
    return Connection()


@fixture(scope="function")
def subscription_model(any_subject):
    return Subscription(subject=any_subject)


@fixture(scope="function")
def publish_model(any_subject):
    return Publish(subject=any_subject)


@fixture(scope="function")
def request_model(any_subject):
    return Request(subject=any_subject)


@fixture(scope="function")
def dummy_cb():
    return


@fixture(scope="function")
def any_subject():
    return "any_subject"


@fixture(scope="function")
def any_token():
    return b"any_token"


@fixture(scope="function")
def any_payload():
    return b"any_payload"


class TestTempStorageHelpers:
    def exceeds_max_payload_size_true_test(self, client):
        # Given
        payload = b"x" * (DEFAULT_MAX_PAYLOAD_SIZE + 1)

        # When
        result = client._exceeds_max_payload_size(payload)

        # Then
        assert result is True

    def exceeds_max_payload_size_false_test(self, client):
        # Given
        payload = b""

        # When
        result = client._exceeds_max_payload_size(payload)

        # Then
        assert result is False

    async def pre_recover_cb__payload_is_stored_test(self, client, any_payload):
        # Given
        client._temp_payload_storage.is_stored = Mock(return_value=True)
        client._temp_payload_storage.recover = Mock(return_value=any_payload)

        async def dummy_cb(msg_: NatsMessage):
            return

        msg = Mock(spec_set=NatsMessage)

        # When
        decorated = client._pre_recover_cb(dummy_cb)
        await decorated(msg)

        # Then
        client._temp_payload_storage.recover.assert_called()
        assert msg.data == any_payload

    async def pre_recover_cb__payload_is_not_stored_test(self, client, any_payload):
        # Given
        client._temp_payload_storage.is_stored = Mock(return_value=False)
        client._temp_payload_storage.recover = Mock()

        async def dummy_cb(msg_: NatsMessage):
            return

        msg = Mock(spec_set=NatsMessage)
        msg.data = any_payload

        # When
        decorated = client._pre_recover_cb(dummy_cb)
        await decorated(msg)

        # Then
        client._temp_payload_storage.recover.assert_not_called()
        assert msg.data == any_payload


class TestConnect:
    async def ok_test(self, client, connection_model):
        # When
        with patch.object(RealClient, "connect") as m:
            await client.connect(**asdict(connection_model))

        # Then
        m.assert_awaited_once_with(**asdict(connection_model))

    async def ko_no_servers_error_test(self, client, connection_model):
        # When
        with patch.object(RealClient, "connect", side_effect=errors.NoServersError):
            # Then
            with raises(NatsConnectionError):
                await client.connect(**asdict(connection_model))

    async def ko_os_error_test(self, client, connection_model):
        # When
        with patch.object(RealClient, "connect", side_effect=OSError):
            # Then
            with raises(NatsConnectionError):
                await client.connect(**asdict(connection_model))

    async def ko_nats_generic_error_test(self, client, connection_model):
        # When
        with patch.object(RealClient, "connect", side_effect=errors.Error):
            # Then
            with raises(NatsConnectionError):
                await client.connect(**asdict(connection_model))

    async def ko_timeout_error_test(self, client, connection_model):
        # When
        with patch.object(RealClient, "connect", side_effect=asyncio.TimeoutError):
            # Then
            with raises(NatsConnectionError):
                await client.connect(**asdict(connection_model))


class TestSubscribe:
    async def ok_test(self, client, subscription_model, dummy_cb):
        # Given
        client._pre_recover_cb = Mock(return_value=dummy_cb)

        # When
        with patch.object(RealClient, "subscribe") as m:
            await client.subscribe(**asdict(subscription_model))

        # Then
        kwargs = {**asdict(subscription_model), "cb": dummy_cb}
        m.assert_awaited_once_with(**kwargs)

    async def ko_nats_conn_closed_error_test(self, client, subscription_model):
        # When
        with patch.object(RealClient, "subscribe", side_effect=errors.ConnectionClosedError):
            # Then
            with raises(NatsConnectionError):
                await client.subscribe(**asdict(subscription_model))

    async def ko_nats_conn_draining_error_test(self, client, subscription_model):
        # When
        with patch.object(RealClient, "subscribe", side_effect=errors.ConnectionDrainingError):
            # Then
            with raises(NatsConnectionError):
                await client.subscribe(**asdict(subscription_model))

    async def ko_bad_subject_error_test(self, client, subscription_model):
        # When
        with patch.object(RealClient, "subscribe", side_effect=errors.BadSubjectError):
            # Then
            with raises(BadSubjectError):
                await client.subscribe(**asdict(subscription_model))


class TestPublish:
    async def ok_large_payload_test(self, client, publish_model, any_token):
        # Given
        client._exceeds_max_payload_size = Mock(return_value=True)
        client._temp_payload_storage.store.return_value = any_token

        # When
        with patch.object(RealClient, "publish") as m:
            await client.publish(**asdict(publish_model))

        # Then
        kwargs = {**asdict(publish_model), "payload": any_token}
        m.assert_awaited_once_with(**kwargs)

    async def ok_tiny_payload_test(self, client, publish_model):
        # Given
        client._exceeds_max_payload_size = Mock(return_value=False)

        # When
        with patch.object(RealClient, "publish") as m:
            await client.publish(**asdict(publish_model))

        # Then
        m.assert_awaited_once_with(**asdict(publish_model))

    async def ko_nats_conn_closed_error_test(self, client, publish_model):
        # When
        with patch.object(RealClient, "publish", side_effect=errors.ConnectionClosedError):
            # Then
            with raises(NatsConnectionError):
                await client.publish(**asdict(publish_model))

    async def ko_nats_conn_draining_error_test(self, client, publish_model):
        # When
        with patch.object(RealClient, "publish", side_effect=errors.ConnectionDrainingError):
            # Then
            with raises(NatsConnectionError):
                await client.publish(**asdict(publish_model))

    async def ko_bad_subject_error_test(self, client, publish_model):
        # When
        with patch.object(RealClient, "publish", side_effect=errors.BadSubjectError):
            # Then
            with raises(BadSubjectError):
                await client.publish(**asdict(publish_model))


class TestRequest:
    async def ok_test(self, client, request_model):
        # Given
        client._temp_payload_storage.is_stored.return_value = False

        nats_msg = Mock(spec_set=NatsMessage)

        # When
        with patch.object(RealClient, "request", new=AsyncMock(return_value=nats_msg)) as m:
            actual = await client.request(**asdict(request_model))

        # Then
        m.assert_awaited_once_with(**asdict(request_model))
        assert actual == nats_msg

    async def ok_large_response_payload_test(self, client, request_model, any_payload):
        # Given
        client._temp_payload_storage.is_stored.return_value = True
        client._temp_payload_storage.recover.return_value = any_payload

        nats_msg = Mock(spec_set=NatsMessage)

        # When
        with patch.object(RealClient, "request", new=AsyncMock(return_value=nats_msg)) as m:
            actual = await client.request(**asdict(request_model))

        # Then
        m.assert_awaited_once_with(**asdict(request_model))
        assert nats_msg.data == any_payload

    async def ko_nats_conn_closed_error_test(self, client, request_model):
        # When
        with patch.object(RealClient, "request", side_effect=errors.ConnectionClosedError):
            # Then
            with raises(NatsConnectionError):
                await client.request(**asdict(request_model))

    async def ko_nats_conn_draining_error_test(self, client, request_model):
        # When
        with patch.object(RealClient, "request", side_effect=errors.ConnectionDrainingError):
            # Then
            with raises(NatsConnectionError):
                await client.request(**asdict(request_model))

    async def ko_bad_subject_error_test(self, client, request_model):
        # When
        with patch.object(RealClient, "request", side_effect=errors.BadSubjectError):
            # Then
            with raises(BadSubjectError):
                await client.request(**asdict(request_model))

    async def ko_timeout_error_test(self, client, request_model):
        # When
        with patch.object(RealClient, "request", side_effect=errors.TimeoutError):
            # Then
            with raises(ResponseTimeoutError):
                await client.request(**asdict(request_model))
