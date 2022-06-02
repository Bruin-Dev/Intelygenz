import json


class DiGiRecoveryLogs:
    def __init__(self, logger, event_bus, digi_repository):
        self._logger = logger
        self._event_bus = event_bus
        self._digi_repository = digi_repository

    async def get_digi_recovery_logs(self, msg: dict):
        request_id = msg["request_id"]
        response_topic = msg["response_topic"]
        response = {"request_id": request_id, "body": None, "status": None}
        if "body" not in msg.keys():
            self._logger.error(f"Cannot reboot DiGi client using {json.dumps(msg)}. " f"JSON malformed")
            response["status"] = 400
            response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(response_topic, response)
            return

        payload = msg["body"]

        results = await self._digi_repository.get_digi_recovery_logs(payload)

        response["body"] = results["body"]
        response["status"] = results["status"]

        await self._event_bus.publish_message(response_topic, response)
        self._logger.info(
            f"DiGi recovery logs retrieved and publishing results in event bus for request {json.dumps(msg)}. "
            f"Message published was {response}"
        )
