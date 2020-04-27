class GetDispatch:

    def __init__(self, logger, config, event_bus, lit_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._lit_repository = lit_repository

    async def get_dispatch(self, msg):
        get_dispatch_response = {"request_id": msg["request_id"], "body": None,
                                 "status": None}
        if msg.get("body") is None:
            get_dispatch_response["status"] = 400
            get_dispatch_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], get_dispatch_response)
            return
        if "dispatch_number" in msg["body"].keys():
            dispatch_number = msg["body"]["dispatch_number"]
            self._logger.info(f"Getting dispatch of dispatch number: {dispatch_number}")
            get_dispatch = self._lit_repository.get_dispatch(dispatch_number)
            get_dispatch_response["body"] = get_dispatch["body"]
            get_dispatch_response["status"] = get_dispatch["status"]

        else:
            self._logger.info("Getting all dispatches")
            get_all_dispatches = self._lit_repository.get_all_dispatches()
            get_dispatch_response["body"] = get_all_dispatches["body"]
            get_dispatch_response["status"] = get_all_dispatches["status"]

        await self._event_bus.publish_message(msg['response_topic'], get_dispatch_response)
