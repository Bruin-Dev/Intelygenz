class IDsBySerialClient:

    def __init__(self, config, logger, velocloud_client, edge_dict_repo):
        self._config = config.VELOCLOUD_CONFIG
        self._logger = logger
        self._velocloud_client = velocloud_client
        self._edge_dict_repository = edge_dict_repo

    async def create_id_by_serial_dict(self):
        id_by_serial_dict = await self._velocloud_client.get_all_enterprises_edges_with_host_by_serial()
        ttl = self._config['ids_by_serial_cache_ttl']
        for serial in id_by_serial_dict:
            self._edge_dict_repository.set_serial_to_edge_list(serial, id_by_serial_dict[serial], ttl)

    async def search_for_edge_id_by_serial(self, serial):
        redis_edge_list = self._edge_dict_repository.get_serial_to_edge_list(serial)

        return redis_edge_list
