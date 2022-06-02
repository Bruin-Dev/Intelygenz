import logging
from datetime import datetime
from typing import List

import aiohttp
from tenacity import RetryError, after_log, retry, stop_after_delay, wait_exponential


class LuminClientError(Exception):
    pass


class LuminBillingClient:
    """
    Simple Client for Lumin.ai billing API
    ---------------------------------------------------------------------------
    requires a customer-specific URI and Token to call the billing data endpoint
    """

    def __init__(self, config: dict, **opts):
        self.config = config
        self.logger = opts.get("logger")
        self.http_client = opts.get("http_client", aiohttp.ClientSession)
        self.headers = opts.get("headers", {})
        self.headers.setdefault("Authorization", f'Bearer {self.config["token"]}')
        self.headers.setdefault("Content-Type", "application/json")

    async def get_billing_data_for_period(
        self,
        billing_types: List[str],
        start: datetime,
        end: datetime,
        start_token: str = "",
    ) -> dict:
        """
        Retrieve billing data for given billing_types, start date and end date
        :param billing_types: list of billing_type strings
        :param start: tz-aware datetime
        :param end: tz-aware datetime
        :param start_token: if paginated, indicates where to continue
        """

        config = self.config

        @retry(
            after=after_log(self.logger, logging.WARNING),
            wait=wait_exponential(multiplier=config["multiplier"], min=config["min"]),
            stop=stop_after_delay(config["stop_delay"]),
        )
        async def do_request(session, data):
            async with session.post(config["uri"], json=data, raise_for_status=True) as r:
                # raise for status to ensure retries
                return await r.json()

        d = {"type": ",".join(billing_types), "start": str(start), "end": str(end)}

        if start_token:
            d["start_token"] = start_token

        async with self.http_client(headers=self.headers) as s:
            try:
                return await do_request(s, d)
            except RetryError as exc:
                # raise as custom error
                msg = "Could not connect to {} with headers {}, body {}".format(self.config["uri"], self.headers, d)

                self.logger.exception(msg)
                raise LuminClientError(msg) from exc
