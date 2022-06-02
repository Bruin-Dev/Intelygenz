import logging
import socket
from datetime import datetime


class HostnameFilter(logging.Filter):
    hostname = socket.gethostname()

    def filter(self, record):
        record.hostname = HostnameFilter.hostname
        return True


class TimeZoneNaiveFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        now = datetime.utcnow()
        return now.strftime("%Y-%m-%d %H:%M:%S")


class LoggerClient:
    def __init__(self, config):
        self._config = config.LOG_CONFIG
        self._environment_name = config.ENVIRONMENT_NAME

    def get_logger(self):
        logger = logging.getLogger(self._config["name"])
        logger.propagate = False
        logger.setLevel(self._config["level"])
        log_handler = self._config["stream_handler"]
        formatter = TimeZoneNaiveFormatter(self._config["format"])
        log_handler.setFormatter(formatter)
        logger.addFilter(HostnameFilter())
        logger.addHandler(log_handler)
        return logger
