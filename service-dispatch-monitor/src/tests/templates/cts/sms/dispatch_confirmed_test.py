from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_12_hours_before_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_2_hours_before_sms_tech
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_12_hours_before_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_2_hours_before_sms


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


expected_tech_12_hours_before_sms = """This is an automated message from MetTel.

A field engineer will arrive in 12 hours, Mar 16, 2020 @ 07:00 AM Eastern, at your location.

You will receive a text message at this number when they have arrived.
"""


def cts_get_tech_12_hours_before_sms_test():
    body = {
        'date_of_dispatch': 'Mar 16, 2020 @ 07:00 AM Eastern'
    }
    tech_12_hours_before_sms = cts_get_tech_12_hours_before_sms(body)

    assert tech_12_hours_before_sms == expected_tech_12_hours_before_sms


expected_tech_12_hours_before_sms_tech = """This is an automated message from MetTel.

You have a dispatch coming up in 12 hours, Mar 16, 2020 @ 07:00 AM Eastern.
For Premier Financial Bancorp at 1501 K St NW
"""


def cts_get_tech_12_hours_before_sms_tech_test():
    body = {
        'date_of_dispatch': 'Mar 16, 2020 @ 07:00 AM Eastern',
        'site': 'Premier Financial Bancorp',
        'street': '1501 K St NW'
    }
    tech_12_hours_before_sms_tech = cts_get_tech_12_hours_before_sms_tech(body)

    assert tech_12_hours_before_sms_tech == expected_tech_12_hours_before_sms_tech


expected_tech_2_hours_before_sms = """This is an automated message from MetTel.

A field engineer will arrive in 2 hours, Mar 16, 2020 @ 07:00 AM Eastern, at your location.

You will receive a text message at this number when they have arrived.
"""


def cts_get_tech_2_hours_before_sms_test():
    body = {
        'date_of_dispatch': 'Mar 16, 2020 @ 07:00 AM Eastern'
    }
    tech_2_hours_before_sms = cts_get_tech_2_hours_before_sms(body)

    assert tech_2_hours_before_sms == expected_tech_2_hours_before_sms


expected_tech_2_hours_before_sms_tech = """This is an automated message from MetTel.

You have a dispatch coming up in 2 hours, Mar 16, 2020 @ 07:00 AM Eastern.
For Premier Financial Bancorp at 1501 K St NW
"""


def cts_get_tech_2_hours_before_sms_tech_test():
    body = {
        'date_of_dispatch': 'Mar 16, 2020 @ 07:00 AM Eastern',
        'site': 'Premier Financial Bancorp',
        'street': '1501 K St NW'
    }
    tech_2_hours_before_sms_tech = cts_get_tech_2_hours_before_sms_tech(body)

    assert tech_2_hours_before_sms_tech == expected_tech_2_hours_before_sms_tech
