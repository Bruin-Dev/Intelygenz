import pytest


@pytest.fixture(scope="session")
def make_report_incident_response():
    def _inner(*, state: str = None):
        return {
            "result": {
                "number": "INC0123456",
                "state": state,
            }
        }

    return _inner
