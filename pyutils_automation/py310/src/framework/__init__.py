import logging


# Initialize root of the loggers' hierarchy with a NullHandler, and delegate its configuration to clients of the
# framework. See https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library.
logging.getLogger('framework').addHandler(logging.NullHandler())
