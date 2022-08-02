from tests.fixtures.domain import AnyEmail


class TestEmail:
    def cc_addresses_are_properly_comma_separated_test(self):
        email = AnyEmail(cc_addresses=["cc_address_1", "cc_address_2"])
        assert email.comma_separated_cc_addresses() == "cc_address_1, cc_address_2"

    def parent_emails_are_properly_detected_test(self):
        assert AnyEmail().is_parent_email

    def reply_emails_are_properly_detected_test(self):
        assert AnyEmail(parent=AnyEmail()).is_reply_email
