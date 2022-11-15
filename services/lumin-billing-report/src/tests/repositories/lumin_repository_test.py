from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from application.repositories.lumin_repository import LuminBillingRepository, LuminBillingTypes


@pytest.fixture
def lumin_client_responses():
    return [
        {
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
        },
        {
            "ok": True,
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
        },
    ]


class TestLuminBillingRepository:
    def instance_test(self):
        lumin_client = MagicMock()
        repo = LuminBillingRepository(lumin_client)
        assert repo.client is lumin_client

    async def get_billing_data_for_period_test(self, lumin_client_responses):
        mock_get = AsyncMock(side_effect=lumin_client_responses)
        lumin_client = MagicMock()
        lumin_client.get_billing_data_for_period = mock_get

        repo = LuminBillingRepository(lumin_client)

        billing_types = [LuminBillingTypes.SCHEDULED.value]
        end = datetime.now(tz=timezone.utc)
        start = end - timedelta(days=30)

        items = await repo.get_billing_data_for_period(billing_types, start, end)

        assert items == lumin_client_responses[0]["items"] + lumin_client_responses[1]["items"]
