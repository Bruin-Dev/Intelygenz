class CancelDispatch:

    def __init__(self, logger, config, event_bus, lit_repository):
        self._logger = logger
        self._config = config
        self._event_bus = event_bus
        self._lit_repository = lit_repository

    async def cancel_dispatch(self, msg):
        cancel_dispatch_response = {
            "request_id": msg["request_id"],
            "body": None,
            "status": None
        }
        if msg.get("body") is None:
            cancel_dispatch_response["status"] = 400
            cancel_dispatch_response["body"] = 'Must include "body" in request'
            await self._event_bus.publish_message(msg['response_topic'], cancel_dispatch_response)
            return
        request_dispatch_payload = msg["body"].get("CancelDispatchRequest")
        if request_dispatch_payload is None:
            cancel_dispatch_response["status"] = 400
            cancel_dispatch_response["body"] = 'Must include "CancelDispatchRequest" in request'
            await self._event_bus.publish_message(msg['response_topic'], cancel_dispatch_response)
            return

        dispatch_required_keys = ["Dispatch_Number", "Cancellation_Reason", "Cancellation_Requested_By"]

        if all(key in request_dispatch_payload.keys() for key in dispatch_required_keys):
            self._logger.info('Requesting cancel a dispatch')
            cancel_dispatch = self._lit_repository.cancel_dispatch(msg["body"])

            if cancel_dispatch["status"] in range(200, 300):
                self._logger.info(f'Requested cancel a dispatch with dispatch number: '
                                  f'{cancel_dispatch["body"]["CancelDispatchServiceResponse"]}')

            cancel_dispatch_response["body"] = cancel_dispatch["body"]
            cancel_dispatch_response["status"] = cancel_dispatch["status"]
        else:
            cancel_dispatch_response["status"] = 400
            cancel_dispatch_response["body"] = f'Must include the following keys in request: {dispatch_required_keys}'
        await self._event_bus.publish_message(msg['response_topic'], cancel_dispatch_response)
