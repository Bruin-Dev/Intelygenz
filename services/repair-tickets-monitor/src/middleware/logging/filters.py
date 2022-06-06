from logging import Filter

from middleware.logging import get_logging_context


class ContextFilter(Filter):
    def filter(self, record):
        logging_context = get_logging_context()
        for key, value in logging_context.items():
            setattr(record, key, value)
        return True
