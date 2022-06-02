import pytest
from config import testconfig


# Factories
@pytest.fixture(scope="session")
def make_email():
    def _inner(*, msg_uid: str = "", message: str = "", body: str = "", subject: str = ""):
        return {
            "msg_uid": msg_uid,
            "message": message,
            "body": body,
            "subject": subject,
        }

    return _inner


# RPC requests
@pytest.fixture(scope="session")
def make_get_unread_emails_request(make_rpc_request):
    def _inner(*, request_id: str = "", email_account: str = None, email_filter: str = None):
        email_account = email_account or testconfig.FRAUD_CONFIG["inbox_email"]
        email_filter = email_filter or testconfig.FRAUD_CONFIG["sender_emails_list"]

        payload = {
            "email_account": email_account,
            "email_filter": email_filter,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


@pytest.fixture(scope="session")
def make_mark_email_as_read_request(make_rpc_request):
    def _inner(*, request_id: str = "", msg_uid: str = "", email_account: str = None):
        email_account = email_account or testconfig.FRAUD_CONFIG["inbox_email"]

        payload = {
            "msg_uid": msg_uid,
            "email_account": email_account,
        }

        return make_rpc_request(
            request_id=request_id,
            **payload,
        )

    return _inner


# RPC responses
@pytest.fixture(scope="session")
def get_unread_emails_response(make_rpc_response):
    return make_rpc_response(
        body=[],
        status=200,
    )


@pytest.fixture(scope="session")
def mark_email_as_read_response(make_rpc_response):
    return make_rpc_response(
        body=None,
        status=204,
    )


@pytest.fixture(scope="session")
def gmail_500_response(make_rpc_response):
    return make_rpc_response(
        body="Internal Server Error",
        status=500,
    )
