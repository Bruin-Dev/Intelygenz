from logging import LoggerAdapter, Logger


class RpcLogger(LoggerAdapter):
    """
    Logger that provides request contextual data.
    """

    def __init__(self, logger: Logger, request_id: str):
        super().__init__(logger=logger, extra={"request_id": request_id})

    def process(self, msg, kwargs):
        extra_str = ', '.join(f"{key}={value}" for key, value in self.extra.items())
        return "[%s] %s" % (extra_str, msg), kwargs
