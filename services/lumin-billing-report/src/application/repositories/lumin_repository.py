from datetime import datetime
from enum import Enum
from typing import List

from application.clients.lumin_client import LuminBillingClient


class LuminBillingTypes(Enum):
    ALL = ""
    DELETE = "billing.delete"
    FATAL_ERROR_USER_ID = "billing.fatal-error.sfdc.user-id"
    LEAD_RECEIVED = "billing.lead-received"
    SCHEDULED = "billing.scheduled"
    RESCHEDULED = "billing.rescheduled"


class LuminBillingRepository:
    def __init__(self, logger, client: LuminBillingClient):
        self.logger = logger
        self.client = client

    async def get_billing_data_for_period(self, billing_types: List[str], start: datetime, end: datetime) -> List[dict]:
        """
        Retrieve all paginated billing data for given billing_types, start date and end date
        :param billing_types: list of billing_type strings
        :param start: tz-aware datetime
        :param end: tz-aware datetime
        :return: iterable of billing data items
        """

        start_token = ""
        ret = []

        while True:
            self.logger.info(
                "fetching billing data for {}".format(
                    {"type": ",".join(billing_types), "start": str(start), "end": str(end), "start_token": start_token}
                )
            )

            body = await self.client.get_billing_data_for_period(billing_types, start, end, start_token)

            ret.extend(body["items"])

            if not body.get("next_token", None):
                break

            start_token = body["next_token"]

        return ret
