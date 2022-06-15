import json
import logging

from nats.aio.msg import Msg

from ..repositories.velocloud_repository import VelocloudRepository

logger = logging.getLogger(__name__)


class EventEdgesForAlert:
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

        if not all(key in payload["body"].keys() for key in ("edge", "start_date", "end_date")):
            response["status"] = 400
            response["body"] = 'Must include "edge", "start_date", "end_date" in request body'
            await msg.respond(json.dumps(response).encode())
            return

        edgeids = payload["body"]["edge"]
        start = payload["body"]["start_date"]
        end = payload["body"]["end_date"]
        limit = None
        filter_ = None

        if "filter" in payload["body"].keys():
            filter_ = payload["body"]["filter"]

        if "limit" in payload["body"].keys():
            limit = payload["body"]["limit"]

        logger.info(f"Sending events for edge with data {edgeids} for alerts")
        events_by_edge = await self._velocloud_repository.get_all_edge_events(
            edge=edgeids,
            start=start,
            end=end,
            filter_events_status_list=filter_,
            limit=limit,
        )
        response["body"] = events_by_edge["body"]
        response["status"] = events_by_edge["status"]

        await msg.respond(json.dumps(response).encode())
        logger.info(
            f"Edge events for alerts published for request {json.dumps(payload)}. Message published was {response}"
        )
