from datetime import datetime

from tests.fixtures.domain import AnyEmail


class TestEmail:
    def cc_addresses_are_properly_comma_separated_test(self):
        email = AnyEmail(cc_addresses=["cc_address_1", "cc_address_2"])
        assert email.comma_separated_cc_addresses() == "cc_address_1, cc_address_2"

    def parent_emails_are_properly_detected_test(self):
        assert AnyEmail().is_parent_email

    def reply_emails_are_properly_detected_test(self):
        assert AnyEmail(parent=AnyEmail()).is_reply_email

    def parent_emails_have_no_reply_interval_test(self):
        assert not AnyEmail().reply_interval

    def reply_intervals_are_properly_calculated_test(self):
        parent_date = datetime(2000, 1, 1, 0, 0, 0)
        reply_date = datetime(2000, 1, 1, 0, 0, 10)
        assert AnyEmail(date=reply_date, parent=AnyEmail(date=parent_date)).reply_interval == 10
