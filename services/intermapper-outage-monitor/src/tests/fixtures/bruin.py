import pytest


@pytest.fixture(scope="session")
def make_post_notification_email_milestone_request(make_rpc_request):
    def _inner(*, request_id: str = "", ticket_id: int = 0, service_number: str = "", notification_type: str = ""):
        payload = {
            "notification_type": notification_type,
            "ticket_id": ticket_id,
            "service_number": service_number,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


# RPC responses
@pytest.fixture(scope="session")
def bruin_generic_200_response(make_rpc_response):
    return make_rpc_response(
        body="ok",
        status=200,
    )


@pytest.fixture(scope="session")
def bruin_500_response(make_rpc_response):
    return make_rpc_response(
        body="Got internal error from Bruin",
        status=500,
    )
