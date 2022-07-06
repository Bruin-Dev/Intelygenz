import json


class ReportIncident:
    def __init__(self, logger, event_bus, servicenow_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._servicenow_repository = servicenow_repository

    async def report_incident(self, msg: dict):
        response = {"request_id": msg["request_id"], "body": None, "status": None}
        body = msg.get("body")

        if body is None:
            response["status"] = 400
            response["body"] = 'Must include "body" in the request'
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        host = body.get("host")
        gateway = body.get("gateway")
        summary = body.get("summary")
        note = body.get("note")

        if not host or not gateway or not summary or not note:
            self._logger.error(f"Cannot report incident using {json.dumps(msg)}. JSON malformed")
            response["body"] = 'You must include "host", "gateway", "summary" and "note" in the request body'
            response["status"] = 400
            await self._event_bus.publish_message(msg["response_topic"], response)
            return

        response = await self._servicenow_repository.report_incident(host, gateway, summary, note)
        self._logger.info(f"Report incident response: {response}")
        await self._event_bus.publish_message(msg["response_topic"], response)
