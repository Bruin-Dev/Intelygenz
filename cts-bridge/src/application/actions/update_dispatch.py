class UpdateDispatch:

    def __init__(self, logger, config, event_bus, cts_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._cts_repository = cts_repository

    async def update_dispatch(self, msg):
        update_dispatch_response = {"request_id": msg["request_id"], "body": None,
                                    "status": None}
        if msg.get("body") is None:
            update_dispatch_response["status"] = 400
            update_dispatch_response["body"] = 'Must include "body' \
                                               '" in request'
            await self._event_bus.publish_message(msg['response_topic'], update_dispatch_response)
            return

        update_dispatch_id = msg["body"].get("dispatch_id")
        if update_dispatch_id is None:
            update_dispatch_response["status"] = 400
            update_dispatch_response["body"] = 'Must include "dispatch_id" in request'
            await self._event_bus.publish_message(msg['response_topic'], update_dispatch_response)
            return

        update_dispatch_payload = msg["body"].get("payload")
        if update_dispatch_payload is None:
            update_dispatch_response["body"] = 'Must include "payload" in request'
            update_dispatch_response["status"] = 400
            await self._event_bus.publish_message(msg['response_topic'], update_dispatch_response)
            return

        self._logger.info(f"Updating dispatch of dispatch number: {update_dispatch_id} ")
        update_dispatch = self._cts_repository.update_dispatch(update_dispatch_id, update_dispatch_payload)
        update_dispatch_response["body"] = update_dispatch["body"]
        update_dispatch_response["status"] = update_dispatch["status"]

        await self._event_bus.publish_message(msg['response_topic'], update_dispatch_response)
