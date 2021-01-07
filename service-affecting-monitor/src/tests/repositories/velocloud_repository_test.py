import asyncio
from unittest.mock import Mock
from unittest.mock import patch, call
from shortuuid import uuid

from application.repositories.velocloud_repository import VelocloudRepository
from config import testconfig


uuid_ = uuid()


class TestVelocloudRepository:
    def instance_test(self):
        event_bus = Mock()
        logger = Mock()
        config = testconfig
        notifications_repository = Mock()

        velocloud_repository = VelocloudRepository(event_bus, logger, config, notifications_repository)

        assert velocloud_repository._event_bus is event_bus
        assert velocloud_repository._logger is logger
        assert velocloud_repository._config is config
        assert velocloud_repository._notifications_repository is notifications_repository
