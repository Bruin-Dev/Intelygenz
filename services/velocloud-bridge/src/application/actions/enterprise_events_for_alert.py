import json
import logging

from nats.aio.msg import Msg

from ..repositories.velocloud_repository import VelocloudRepository

logger = logging.getLogger(__name__)


class EventEnterpriseForAlert:
    def __init__(self, velocloud_repository: VelocloudRepository):
        self._velocloud_repository = velocloud_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"body": None, "status": None}

        if payload.get("body") is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await msg.respond(json.dumps(response).encode())
            return

        if not all(key in payload["body"].keys() for key in ("enterprise_id", "host", "start_date", "end_date")):
            response["status"] = 400
            response["body"] = 'Must include "enterprise_id", "host", "start_date", "end_date" in request in body'
            await msg.respond(json.dumps(response).encode())
            return

        enterprise_id = payload["body"]["enterprise_id"]
        host = payload["body"]["host"]
        start = payload["body"]["start_date"]
        end = payload["body"]["end_date"]
        limit = None
        filter_ = None

        if "filter" in payload["body"].keys():
            filter_ = payload["body"]["filter"]

        if "limit" in payload["body"].keys():
            limit = payload["body"]["limit"]

        logger.info(f"Sending events for enterprise with data {enterprise_id} for alerts")
        events_by_enterprise = await self._velocloud_repository.get_all_enterprise_events(
            enterprise=enterprise_id,
            host=host,
            start=start,
            end=end,
            filter_events_status_list=filter_,
            limit=limit,
        )
        response["body"] = events_by_enterprise["body"]
        response["status"] = events_by_enterprise["status"]

        await msg.respond(json.dumps(response).encode())
        logger.info(
            f"Enterprise events for alerts published for request {json.dumps(payload)}. "
            f"Message published was {response}"
        )
