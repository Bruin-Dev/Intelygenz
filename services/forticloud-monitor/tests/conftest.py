import logging
import os
from unittest.mock import Mock

import pytest
import shortuuid

shortuuid.uuid = Mock(return_value="any_uuid")
logging.getLogger = Mock()


os.environ["NATS_SERVERS"] = '["any_server"]'


@pytest.fixture
def any_exception():
    class AnyException(Exception):
        pass
    return AnyException
