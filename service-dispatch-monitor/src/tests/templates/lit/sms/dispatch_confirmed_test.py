from application.templates.lit.sms.dispatch_confirmed import lit_get_dispatch_confirmed_sms, \
    lit_get_dispatch_confirmed_sms_tech, lit_get_tech_x_hours_before_sms_tech
from application.templates.lit.sms.dispatch_confirmed import lit_get_tech_x_hours_before_sms, \
     lit_get_dispatch_field_engineer_confirmed_sms


expected_dispatch_confirmed_sms = """This is an automated message from MetTel.

A dispatch has been confirmed for your location on 2019-11-14 @ 6PM-8PM Pacific Time.
"""


def lit_get_dispatch_confirmed_sms_test():
    body = {
        'date_of_dispatch': '2019-11-14 @ 6PM-8PM Pacific Time',
    }
    dispatch_confirmed_sms = lit_get_dispatch_confirmed_sms(body)

    assert dispatch_confirmed_sms == expected_dispatch_confirmed_sms


expected_field_engineer_confirmed_sms = """This is an automated message from MetTel.

A field engineer has been assigned for your location on 2019-11-14 @ 6PM-8PM Pacific Time.
The field engineer handling this dispatch will be Fred Test.
"""


def lit_get_dispatch_field_engineer_confirmed_sms_test():
    body = {
        'date_of_dispatch': '2019-11-14 @ 6PM-8PM Pacific Time',
        'tech_name': 'Fred Test'
    }
    dispatch_field_engineer_confirmed = lit_get_dispatch_field_engineer_confirmed_sms(body)
    assert dispatch_field_engineer_confirmed == expected_field_engineer_confirmed_sms


expected_dispatch_confirmed_sms_tech = """This is an automated message from MetTel.

You have been confirmed for a dispatch on 2019-11-14 @ 6PM-8PM Pacific Time.
For me test at 160 Broadway
"""


def lit_get_dispatch_confirmed_sms_tech_test():
    body = {
        'date_of_dispatch': '2019-11-14 @ 6PM-8PM Pacific Time',
        'site': 'me test',
        'street': '160 Broadway'
    }
    dispatch_confirmed_sms_tech = lit_get_dispatch_confirmed_sms_tech(body)

    assert dispatch_confirmed_sms_tech == expected_dispatch_confirmed_sms_tech


expected_tech_12_hours_before_sms = """This is an automated message from MetTel.

A field engineer will arrive in 12 hours, 2019-11-14 @ 6PM-8PM Pacific Time, at your location.

You will receive a text message at this number when they have arrived.
"""


def lit_get_tech_12_hours_before_sms_test():
    body = {
        'date_of_dispatch': '2019-11-14 @ 6PM-8PM Pacific Time',
        'hours': '12',
    }
    tech_12_hours_before_sms = lit_get_tech_x_hours_before_sms(body)

    assert tech_12_hours_before_sms == expected_tech_12_hours_before_sms


expected_tech_2_hours_before_sms = """This is an automated message from MetTel.

A field engineer will arrive in 2 hours, 2019-11-14 @ 6PM-8PM Pacific Time, at your location.

You will receive a text message at this number when they have arrived.
"""


expected_tech_12_hours_before_sms_tech = """This is an automated message from MetTel.

You have a dispatch coming up in 12 hours, 2019-11-14 @ 6PM-8PM Pacific Time.
For me test at 160 Broadway
"""


def lit_get_tech_12_hours_before_sms_tech_test():
    body = {
        'date_of_dispatch': '2019-11-14 @ 6PM-8PM Pacific Time',
        'site': 'me test',
        'street': '160 Broadway',
        'hours': '12',

    }
    tech_12_hours_before_sms_tech = lit_get_tech_x_hours_before_sms_tech(body)

    assert tech_12_hours_before_sms_tech == expected_tech_12_hours_before_sms_tech


expected_tech_2_hours_before_sms = """This is an automated message from MetTel.

A field engineer will arrive in 2 hours, 2019-11-14 @ 6PM-8PM Pacific Time, at your location.

You will receive a text message at this number when they have arrived.
"""


def lit_get_tech_2_hours_before_sms_test():
    body = {
        'date_of_dispatch': '2019-11-14 @ 6PM-8PM Pacific Time',
        'hours': '2',

    }
    tech_2_hours_before_sms = lit_get_tech_x_hours_before_sms(body)

    assert tech_2_hours_before_sms == expected_tech_2_hours_before_sms


expected_tech_2_hours_before_sms_tech = """This is an automated message from MetTel.

You have a dispatch coming up in 2 hours, 2019-11-14 @ 6PM-8PM Pacific Time.
For me test at 160 Broadway
"""


def lit_get_tech_2_hours_before_sms_tech_test():
    body = {
        'date_of_dispatch': '2019-11-14 @ 6PM-8PM Pacific Time',
        'site': 'me test',
        'street': '160 Broadway',
        'hours': '2',
    }
    tech_2_hours_before_sms_tech = lit_get_tech_x_hours_before_sms_tech(body)

    assert tech_2_hours_before_sms_tech == expected_tech_2_hours_before_sms_tech
