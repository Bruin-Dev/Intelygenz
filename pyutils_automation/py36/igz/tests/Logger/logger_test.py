import logging

from igz.config import testconfig as config
from igz.packages.Logger.logger_client import LoggerClient


class TestLoggerClient:
    def instantiation_test(self):
        test_log = LoggerClient(config)
        assert test_log._config == config.LOG_CONFIG
        assert test_log._environment_name == config.ENVIRONMENT_NAME

    def get_logger_test(self):
        test_log = LoggerClient(config).get_logger()
        assert isinstance(test_log, logging._loggerClass) is True
        assert test_log.hasHandlers() is True
        assert test_log.getEffectiveLevel() is 10
