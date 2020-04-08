class UpdateDispatch:

    def __init__(self, logger, config, event_bus, lit_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._lit_repository = lit_repository

    async def update_dispatch(self, msg):
        update_dispatch_response = {"request_id": msg["request_id"], "body": None,
                                    "status": None}
        if msg.get("body") is None:
            update_dispatch_response["status"] = 400
            update_dispatch_response["body"] = 'Must include "body' \
                                               '" in request'
            await self._event_bus.publish_message(msg['response_topic'], update_dispatch_response)
            return
        update_dispatch_payload = msg["body"].get("RequestDispatch")

        if update_dispatch_payload is None:
            update_dispatch_response["status"] = 400
            update_dispatch_response["body"] = 'Must include "RequestDispatch" in request'
            await self._event_bus.publish_message(msg['response_topic'], update_dispatch_response)
            return
        if "dispatch_number" in update_dispatch_payload.keys():
            update_dispatch_payload = {k.lower(): v for k, v in update_dispatch_payload.items()}
            self._logger.info(f"Updating dispatch of dispatch number: {update_dispatch_payload['dispatch_number']} ")
            update_dispatch = self._lit_repository.update_dispatch(msg["body"])
            update_dispatch_response["body"] = update_dispatch["body"]
            update_dispatch_response["status"] = update_dispatch["status"]
        else:
            update_dispatch_response["body"] = 'Must include "Dispatch_Number" in request'
            update_dispatch_response["status"] = 400
        await self._event_bus.publish_message(msg['response_topic'], update_dispatch_response)
