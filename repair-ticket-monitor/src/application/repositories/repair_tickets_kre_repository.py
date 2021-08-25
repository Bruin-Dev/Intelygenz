from typing import List


class RepairTicketsKRERepository:
    def __init__(self, logger, config, notifications_repository):
        self._logger = logger
        self._config = config
        self._notifications_repository = notifications_repository
