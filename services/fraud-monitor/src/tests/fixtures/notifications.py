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
    def _inner(*, request_id: str = "", email_account: str = None, email_filter: str = None, lookup_days: int = None):
        email_account = email_account or testconfig.FRAUD_CONFIG["inbox_email"]
        email_filter = email_filter or testconfig.FRAUD_CONFIG["sender_emails_list"]
        lookup_days = lookup_days or testconfig.FRAUD_CONFIG["alerts_lookup_days"]

        payload = {
            "email_account": email_account,
            "email_filter": email_filter,
            "lookup_days": lookup_days,
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
            "email_account": email_account,
            "msg_uid": msg_uid,
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
