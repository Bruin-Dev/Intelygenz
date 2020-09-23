from unittest.mock import Mock

from config import testconfig
from application.repositories.cts_repository import CtsRepository


class TestCtsRepository:

    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        cts_repository = CtsRepository(logger, config, event_bus, notifications_repository)

        assert cts_repository._event_bus is event_bus
        assert cts_repository._logger is logger
        assert cts_repository._config is config
        assert cts_repository._notifications_repository is notifications_repository
