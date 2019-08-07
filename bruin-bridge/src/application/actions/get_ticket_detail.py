class GetTicketDetail:

    def __init__(self, logger, config, event_bus, bruin_client):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._bruin_client = bruin_client
