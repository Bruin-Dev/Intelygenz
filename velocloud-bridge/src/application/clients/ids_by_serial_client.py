from tenacity import retry, wait_exponential, stop_after_delay


class IDsBySerialClient:

    def __init__(self, config, logger, velocloud_client):
        self._config = config.VELOCLOUD_CONFIG
        self._logger = logger
        self._velocloud_client = velocloud_client
        self._id_by_serial_dict = {}

    async def create_id_by_serial_dict(self):
        self._id_by_serial_dict = {}
        self._id_by_serial_dict = await self._velocloud_client.get_all_enterprises_edges_with_host_by_serial()

    async def search_for_edge_id_by_serial(self, serial):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'],
                                     min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        async def search_for_edge_id_by_serial():
            if serial in self._id_by_serial_dict.keys():
                return self._id_by_serial_dict[serial]
            else:
                self._logger.error('Error 404, serial not found. Retrying call again')
                raise Exception
        return await search_for_edge_id_by_serial()
