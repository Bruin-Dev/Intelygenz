import json
import logging

from nats.aio.msg import Msg

log = logging.getLogger(__name__)


class ReportIncident:
    def __init__(self, event_bus, servicenow_repository):
        self._event_bus = event_bus
        self._servicenow_repository = servicenow_repository

    async def __call__(self, msg: Msg):
        payload = json.loads(msg.data)

        response = {"request_id": payload["request_id"], "body": None, "status": None}
        body = payload.get("body")

        if body is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in the request'
            await msg.respond(json.dumps(response).encode())
            return

        host = body.get("host")
        gateway = body.get("gateway")
        summary = body.get("summary")
        note = body.get("note")
        link = body.get("link")

        if not host or not gateway or not summary or not note or not link:
            log.error(f"Cannot report incident using {json.dumps(payload)}. JSON malformed")
            response["body"] = 'You must include "host", "gateway", "summary", "note" and "link" in the request body'
            response["status"] = 400
            await msg.respond(json.dumps(response).encode())
            return

        response = await self._servicenow_repository.report_incident(host, gateway, summary, note, link)
        log.info(f"Report incident response: {response}")
        await msg.respond(json.dumps(response).encode())
