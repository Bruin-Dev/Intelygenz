from shortuuid import uuid


class LitMonitorRepository:
    def __init__(self, logger, event_bus):
        self._logger = logger
        self._event_bus = event_bus

    async def get_all_dispatches(self):
        payload = {"request_id": uuid(), "body": {}}
        response = await self._event_bus.rpc_request("lit.dispatch.get", payload, timeout=30)

        if 'body' not in response \
                or 'Status' not in response['body'] \
                or 'DispatchList' not in response['body'] \
                or response['body']['Status'] != "Success" \
                or response['body']['DispatchList'] is None:
            self._logger.error(f"[get_all_dispatches] "
                               f"Could not retrieve all dispatches, reason: {response['body']}")
            # TODO: notify slack
            return []

        self._logger.info(f"Retrieved {len(response['body']['DispatchList'])} dispatches.")
        dispatches = response['body']['DispatchList']
        return dispatches
