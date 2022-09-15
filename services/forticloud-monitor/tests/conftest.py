import logging
from dataclasses import dataclass, field
from unittest.mock import Mock

import shortuuid

shortuuid.uuid = Mock(return_value="any_uuid")
logging.getLogger = Mock()


@dataclass
class LoggerMock:
    exception: Mock = field(default_factory=Mock)

    def configure(self, log: Mock):
        log.exception = self.exception


class CustomException(Exception):
    pass
