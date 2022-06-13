import sys
from logging import StreamHandler
from logging.handlers import SysLogHandler


class Stdout(StreamHandler):
    def __init__(self):
        super().__init__(stream=sys.stdout)


class Papertrail(SysLogHandler):
    def __init__(self, *, host: str, port: int):
        super().__init__(address=(host, port))
