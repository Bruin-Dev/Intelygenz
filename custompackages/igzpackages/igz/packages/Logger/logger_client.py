import logging
import sys


class LoggerClient:

    def create_logger(self, name):
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        info_stream = logging.StreamHandler(sys.stdout)
        format = logging.Formatter('%(asctime)s: %(module)s: %(levelname)s: %(message)s')
        info_stream.setFormatter(format)
        logger.addHandler(info_stream)
        return logger
