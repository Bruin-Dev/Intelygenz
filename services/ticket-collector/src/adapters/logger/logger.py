def get_logger():
    from igz.packages.Logger.logger_client import LoggerClient
    from adapters.config import settings
    return LoggerClient(settings).get_logger()
