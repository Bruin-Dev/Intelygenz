class UploadFile:

    def __init__(self, logger, config, event_bus, lit_repository):
        self._config = config
        self._logger = logger
        self._event_bus = event_bus
        self._lit_repository = lit_repository
