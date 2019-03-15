from igz.packages.Logger.logger_client import LoggerClient
from igz.config import testconfig as config
import logging


class TestLoggerClient:

    def instantiation_test(self):
        test_log = LoggerClient(config)
        assert test_log._config == config.LOG_CONFIG

    def get_logger_test(self):
        test_log = LoggerClient(config).get_logger()
        # Checks to see if test_log is a logger
        assert isinstance(test_log, logging._loggerClass) is True
        # Checks to see if handlers exist
        assert test_log.hasHandlers() is True
        # Checks to see if test_log is on the Debug level
        assert test_log.getEffectiveLevel() is 10
