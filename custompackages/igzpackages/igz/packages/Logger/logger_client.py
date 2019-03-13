import logging
import sys


class LoggerClient:

    def create_logger(self, name, output, level):
        logger = logging.getLogger(name)
        stream_handler = logging.StreamHandler(output)
        format = logging.Formatter('%(asctime)s: %(module)s: %(message)s')
        stream_handler.setFormatter(format)
        logger.setLevel(level)
        logger.addHandler(stream_handler)
        return logger
