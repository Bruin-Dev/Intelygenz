from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

import pytest
from aioresponses import aioresponses
from application.clients.lumin_client import LuminBillingClient, LuminClientError
from config.testconfig import LUMIN_CONFIG as testconfig


@pytest.fixture
def test_config():
    return testconfig


@pytest.fixture
def mock_response():
    return {
        "ok": True,
        "next_token": "foo",
        "items": [
            {
                "conversation_id": "5735605401026560",
                "host_did": "199234567890",
                "host_id": "default",
                "id": "MDAwMDAwMDAwMDAwMDAwMDYyODQwNTU1NDQ4NTY1NzY=",
                "timestamp": "2019-02-24T21:29:36.798081+00:00",
                "type": "billing.scheduled",
            },
            {
                "conversation_id": "5711381785477120",
                "host_did": "199234567890",
                "host_id": "default",
                "id": "MDAwMDAwMDAwMDAwMDAwMDYzMDY4ODc1OTEwMDIxMTI=",
                "timestamp": "2019-02-24T21:36:01.295808+00:00",
                "type": "billing.scheduled",
            },
        ],
    }


@pytest.mark.asyncio
class TestLuminBillingClient:
    def instance_test(self, test_config):
        logger = Mock()
        client = LuminBillingClient(test_config, logger=logger)

        assert client.logger is logger

    def check_headers_test(self, test_config):
        logger = Mock()
        client = LuminBillingClient(test_config, logger=logger)

        assert isinstance(client.headers, dict)
        assert "Bearer" in client.headers["Authorization"]
        assert "foobarbaz" in client.headers["Authorization"]

    async def get_billing_data_for_period_test(self, test_config, mock_response):
        with aioresponses() as m:
            m.post(test_config["uri"], payload=mock_response)

            logger = Mock()
            client = LuminBillingClient(test_config, logger=logger)

            billing_types = ["billing.scheduled"]
            end = datetime.now(tz=timezone.utc)
            start = end - timedelta(days=30)
            start_token = "foo"

            result = await client.get_billing_data_for_period(billing_types, start, end, start_token)
            assert result == mock_response

    async def get_billing_data_for_period_non_200_status_test(self, test_config):
        with aioresponses() as m:
            m.post(test_config["uri"], status=400)

            logger = Mock()
            client = LuminBillingClient(test_config, logger=logger)

            billing_types = ["billing.scheduled"]
            end = datetime.now(tz=timezone.utc)
            start = end - timedelta(days=30)
            start_token = "foo"

            with pytest.raises(LuminClientError):
                assert await client.get_billing_data_for_period(billing_types, start, end, start_token)
