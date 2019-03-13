import logging
import sys


class LoggerClient:

    def create_logger(self, name, output, formatter, level):
        logger = logging.getLogger(name)
        stream_handler = logging.StreamHandler(output)
        stream_handler.setFormatter(formatter)
        logger.setLevel(level)
        logger.addHandler(stream_handler)
        return logger
