import logging
import socket
from datetime import datetime
from logging.handlers import SysLogHandler


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

    _config = None

    def __init__(self, config):
        self._config = config.LOG_CONFIG
        self._environment_name = config.ENVIRONMENT_NAME

    def _add_papertrail_log_to_logger(self, logger):
        syslog = SysLogHandler(address=(self._config["papertrail"]["host"], self._config["papertrail"]["port"]))
        syslog.setLevel(self._config["level"])
        format_string = (
            f"%(asctime)s: {self._environment_name}: %(hostname)s: "
            f"{self._config['papertrail']['prefix']}:"
            f" %(module)s::%(lineno)d %(levelname)s: %(message)s"
        )
        syslog_formatter = TimeZoneNaiveFormatter(format_string)
        syslog.setFormatter(syslog_formatter)
        syslog.addFilter(HostnameFilter())
        logger.addHandler(syslog)

    def get_logger(self):
        logger = logging.getLogger(self._config["name"])
        logger.setLevel(self._config["level"])
        log_handler = self._config["stream_handler"]
        formatter = TimeZoneNaiveFormatter(self._config["format"])
        log_handler.setFormatter(formatter)
        logger.addFilter(HostnameFilter())
        logger.addHandler(log_handler)
        if self._config["papertrail"]["active"]:
            self._add_papertrail_log_to_logger(logger)
        return logger
