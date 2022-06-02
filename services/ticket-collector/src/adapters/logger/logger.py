def get_logger():
    from adapters.config import settings
    from igz.packages.Logger.logger_client import LoggerClient

    return LoggerClient(settings).get_logger()
