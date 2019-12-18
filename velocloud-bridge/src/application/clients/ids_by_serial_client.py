from tenacity import retry, wait_exponential, stop_after_delay


class IDsBySerialClient:

    def __init__(self, config, logger, velocloud_client):
        self._config = config.VELOCLOUD_CONFIG
        self._logger = logger
        self._velocloud_client = velocloud_client
        self._id_by_serial_dict = {}

    def create_id_by_serial_dict(self):
        edge_list = self._velocloud_client.get_all_enterprises_edges_with_host()
        for edge in edge_list:
            serial_id = self._velocloud_client.get_edge_information(edge)['serialNumber']
            self._id_by_serial_dict[serial_id] = edge

    def search_for_edge_id_by_serial(self, serial):
        @retry(wait=wait_exponential(multiplier=self._config['multiplier'],
                                     min=self._config['min']),
               stop=stop_after_delay(self._config['stop_delay']))
        def search_for_edge_id_by_serial():
            if serial in self._id_by_serial_dict.keys():
                return self._id_by_serial_dict[serial]
            else:
                self._logger.error('Error 404, serial not found. Retrying call again')
                raise Exception
