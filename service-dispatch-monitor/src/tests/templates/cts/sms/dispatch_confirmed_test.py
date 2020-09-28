from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech


expected_dispatch_confirmed_sms = """This is an automated message from MetTel.

A dispatch has been confirmed for your location on Mar 16, 2020 @ 07:00 AM Eastern.
The field engineer handling this dispatch will be Larry Andershock.
"""


def cts_get_dispatch_confirmed_sms_test():
    body = {
        'date_of_dispatch': 'Mar 16, 2020 @ 07:00 AM Eastern',
        'tech_name': 'Larry Andershock'
    }
    dispatch_confirmed_sms = cts_get_dispatch_confirmed_sms(body)

    assert dispatch_confirmed_sms == expected_dispatch_confirmed_sms


expected_dispatch_confirmed_sms_tech = """This is an automated message from MetTel.

You have been confirmed for a dispatch on Mar 16, 2020 @ 07:00 AM Eastern.
For Premier Financial Bancorp at 1501 K St NW
"""


def cts_get_dispatch_confirmed_sms_tech_test():
    body = {
        'date_of_dispatch': 'Mar 16, 2020 @ 07:00 AM Eastern',
        'site': 'Premier Financial Bancorp',
        'street': '1501 K St NW'
    }
    dispatch_confirmed_sms_tech = cts_get_dispatch_confirmed_sms_tech(body)

    assert dispatch_confirmed_sms_tech == expected_dispatch_confirmed_sms_tech
