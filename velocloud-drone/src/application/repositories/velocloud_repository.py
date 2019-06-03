class VelocloudRepository:
    _config = None
    _clients = None
    _velocloud_client = None
    _logger = None

    def __init__(self, config, logger, velocloud_client):
        self._config = config.VELOCLOUD_CONFIG
        self._logger = logger
        self._velocloud_client = velocloud_client

    def connect_to_all_servers(self):
        self._logger.info('Instantiating and connecting clients in velocloud bridge')
        self._velocloud_client.instantiate_and_connect_clients()

    def get_all_enterprises_edges_with_host(self):
        self._logger.info('Getting all enterprises edges with host')
        return self._velocloud_client.get_all_enterprises_edges_with_host()

    def get_all_hosts_edge_count(self):
        self._logger.info('Getting edge count from host')
        return self._velocloud_client.get_all_hosts_edge_count()

    def get_edge_information(self, host, enterpriseid, edgeid):
        self._logger.info(f'Getting edge information from edge:{edgeid} in enterprise:{enterpriseid} from host:{host}')
        return self._velocloud_client.get_edge_information(host, enterpriseid, edgeid)

    def get_link_information(self, host, enterpriseid, edgeid):
        self._logger.info(f'Getting link information from edge:{edgeid} in enterprise:{enterpriseid} from host:{host}')
        return self._velocloud_client.get_link_information(host, enterpriseid, edgeid)

    def get_enterprise_information(self, host, enterpriseid):
        self._logger.info(f'Getting enterprise information from enterprise:{enterpriseid} in host:{host}')
        return self._velocloud_client.get_enterprise_information(host, enterpriseid)
