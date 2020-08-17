from application.templates.cts.sms.updated_tech import cts_get_updated_tech_sms
from application.templates.cts.sms.updated_tech import cts_get_updated_tech_sms_tech


expected_updated_tech_sms = """This is an automated message from MetTel.

The field engineer handling your dispatch on 2019-11-14 @ 6PM-8PM Pacific Time has changed.
The new field engineer will be: Larry Andershock
"""


def cts_get_updated_tech_sms_test():
    body = {
        'date_of_dispatch': '2019-11-14 @ 6PM-8PM Pacific Time',
        'tech_name': 'Larry Andershock'
    }
    updated_tech_sms = cts_get_updated_tech_sms(body)

    assert updated_tech_sms == expected_updated_tech_sms


expected_updated_tech_sms_tech = """This is an automated message from MetTel.

You have been confirmed for a dispatch on 2019-11-14 @ 6PM-8PM Pacific Time.
For me test at 160 Broadway
"""


def cts_get_updated_tech_sms_tech_test():
    body = {
        'date_of_dispatch': '2019-11-14 @ 6PM-8PM Pacific Time',
        'site': 'me test',
        'street': '160 Broadway'
    }
    updated_tech_sms_tech = cts_get_updated_tech_sms_tech(body)

    assert updated_tech_sms_tech == expected_updated_tech_sms_tech
