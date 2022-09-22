import pytest


@pytest.fixture
def any_exception():
    class AnyException(Exception):
        pass
    return AnyException
