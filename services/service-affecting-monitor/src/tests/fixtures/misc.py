from unittest.mock import Mock

import pytest
from tests.fixtures._constants import CURRENT_DATETIME


@pytest.fixture(scope="session")
def frozen_datetime():
    dt_mock = Mock()
    dt_mock.now.return_value = CURRENT_DATETIME
    return dt_mock
