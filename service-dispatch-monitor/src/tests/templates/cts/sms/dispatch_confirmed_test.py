from application.templates.cts.sms.dispatch_confirmed import cts_get_dispatch_confirmed_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_12_hours_before_sms
from application.templates.cts.sms.dispatch_confirmed import cts_get_tech_2_hours_before_sms


expected_dispatch_confirmed_sms = """This is an automated message from MetTel customer support.

A dispatch has been confirmed for your location on 2020-06-23T14:00:00.000+0000.
"""


def cts_get_dispatch_confirmed_sms_test():
    body = {
        'date_of_dispatch': '2020-06-23T14:00:00.000+0000',
        'time_of_dispatch': '6PM-8PM',
        'time_zone': 'Pacific Time'
    }
    dispatch_confirmed_sms = cts_get_dispatch_confirmed_sms(body)

    assert dispatch_confirmed_sms == expected_dispatch_confirmed_sms


expected_tech_12_hours_before_sms = """This is an automated message from MetTel customer support.

A field engineer will arrive in 12 hours, 2020-06-23T14:00:00.000+0000, at your location.

You will receive a text message at this number when they have arrived.
"""


def cts_get_tech_12_hours_before_sms_test():
    body = {
        'date_of_dispatch': '2020-06-23T14:00:00.000+0000',
        'time_of_dispatch': '6PM-8PM',
        'time_zone': 'Pacific Time'
    }
    tech_12_hours_before_sms = cts_get_tech_12_hours_before_sms(body)

    assert tech_12_hours_before_sms == expected_tech_12_hours_before_sms


expected_tech_2_hours_before_sms = """This is an automated message from MetTel customer support.

A field engineer will arrive in 2 hours, 2020-06-23T14:00:00.000+0000, at your location.

You will receive a text message at this number when they have arrived.
"""


def cts_get_tech_2_hours_before_sms_test():
    body = {
        'date_of_dispatch': '2020-06-23T14:00:00.000+0000',
        'time_of_dispatch': '6PM-8PM',
        'time_zone': 'Pacific Time'
    }
    tech_2_hours_before_sms = cts_get_tech_2_hours_before_sms(body)

    assert tech_2_hours_before_sms == expected_tech_2_hours_before_sms
