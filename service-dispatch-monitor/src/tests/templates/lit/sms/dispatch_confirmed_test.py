from application.templates.lit.sms.dispatch_confirmed import lit_get_dispatch_confirmed_sms, \
    lit_get_dispatch_confirmed_sms_tech, lit_get_tech_12_hours_before_sms_tech, lit_get_tech_2_hours_before_sms_tech
from application.templates.lit.sms.dispatch_confirmed import lit_get_tech_12_hours_before_sms
from application.templates.lit.sms.dispatch_confirmed import lit_get_tech_2_hours_before_sms


expected_dispatch_confirmed_sms = """This is an automated message from MetTel.

A dispatch has been confirmed for your location on 2020-03-16 16:00:00 PDT.
The field engineer handling this dispatch will be Larry Andershock.
"""


def lit_get_dispatch_confirmed_sms_test():
    body = {
        'date_of_dispatch': '2020-03-16 16:00:00 PDT',
        'tech_name': 'Larry Andershock'
    }
    dispatch_confirmed_sms = lit_get_dispatch_confirmed_sms(body)

    assert dispatch_confirmed_sms == expected_dispatch_confirmed_sms


expected_dispatch_confirmed_sms_tech = """This is an automated message from MetTel.

You have been confirmed for a dispatch on 2020-03-16 16:00:00 PDT.
For me test at 160 Broadway
"""


def lit_get_dispatch_confirmed_sms_tech_test():
    body = {
        'date_of_dispatch': '2020-03-16 16:00:00 PDT',
        'site': 'me test',
        'street': '160 Broadway'
    }
    dispatch_confirmed_sms_tech = lit_get_dispatch_confirmed_sms_tech(body)

    assert dispatch_confirmed_sms_tech == expected_dispatch_confirmed_sms_tech


expected_tech_12_hours_before_sms = """This is an automated message from MetTel.

A field engineer will arrive in 12 hours, 2020-03-16 16:00:00 PDT, at your location.

You will receive a text message at this number when they have arrived.
"""


def lit_get_tech_12_hours_before_sms_test():
    body = {
        'date_of_dispatch': '2020-03-16 16:00:00 PDT'
    }
    tech_12_hours_before_sms = lit_get_tech_12_hours_before_sms(body)

    assert tech_12_hours_before_sms == expected_tech_12_hours_before_sms


expected_tech_2_hours_before_sms = """This is an automated message from MetTel customer support.

A field engineer will arrive in 2 hours, 2020-03-16 16:00:00 PDT, at your location.

You will receive a text message at this number when they have arrived.
"""


expected_tech_12_hours_before_sms_tech = """This is an automated message from MetTel.

You have a dispatch coming up in 12 hours, 2020-03-16 16:00:00 PDT.
For me test at 160 Broadway
"""


def lit_get_tech_12_hours_before_sms_tech_test():
    body = {
        'date_of_dispatch': '2020-03-16 16:00:00 PDT',
        'site': 'me test',
        'street': '160 Broadway'
    }
    tech_12_hours_before_sms_tech = lit_get_tech_12_hours_before_sms_tech(body)

    assert tech_12_hours_before_sms_tech == expected_tech_12_hours_before_sms_tech


expected_tech_2_hours_before_sms = """This is an automated message from MetTel.

A field engineer will arrive in 2 hours, 2020-03-16 16:00:00 PDT, at your location.

You will receive a text message at this number when they have arrived.
"""


def lit_get_tech_2_hours_before_sms_test():
    body = {
        'date_of_dispatch': '2020-03-16 16:00:00 PDT'
    }
    tech_2_hours_before_sms = lit_get_tech_2_hours_before_sms(body)

    assert tech_2_hours_before_sms == expected_tech_2_hours_before_sms


expected_tech_2_hours_before_sms_tech = """This is an automated message from MetTel.

You have a dispatch coming up in 2 hours, 2020-03-16 16:00:00 PDT.
For me test at 160 Broadway
"""


def lit_get_tech_2_hours_before_sms_tech_test():
    body = {
        'date_of_dispatch': '2020-03-16 16:00:00 PDT',
        'site': 'me test',
        'street': '160 Broadway'
    }
    tech_2_hours_before_sms_tech = lit_get_tech_2_hours_before_sms_tech(body)

    assert tech_2_hours_before_sms_tech == expected_tech_2_hours_before_sms_tech
