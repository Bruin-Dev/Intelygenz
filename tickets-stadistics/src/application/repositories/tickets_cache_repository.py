class TicketsCacheRepository:
    nats_error_response = {'body': None, 'status': 503}

    def __init__(self, event_bus, logger, config):
        self._event_bus = event_bus
        self._logger = logger
        self._config = config

    async def get_cache(self):
        err_msg = None

        try:
            response = await self._event_bus.rpc_request("customer.cache.get", "*", timeout=60)
        except Exception as e:
            err_msg = f'An error occurred when requesting customer cache -> {e}'
            response = self.nats_error_response
        else:
            response_body = response['body']
            response_status = response['status']

            if response_status == 202:
                err_msg = response_body

        if err_msg:
            self._logger.error(err_msg)

        return response
