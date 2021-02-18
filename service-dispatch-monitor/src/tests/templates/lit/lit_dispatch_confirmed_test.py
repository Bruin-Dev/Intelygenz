from application.templates.lit.lit_dispatch_confirmed import lit_get_dispatch_confirmed_note
from application.templates.lit.lit_dispatch_confirmed import lit_get_tech_x_hours_before_sms_note

expected_dispatch_confirmed_note = """#*MetTel's IPA*# DIS37266
Dispatch Management - Dispatch Confirmed
Dispatch scheduled for 2019-11-14 @ 6PM-8PM Pacific Time
"""


def lit_get_dispatch_requested_note_test():
    body = {
      'dispatch_number': 'DIS37266',
      'date_of_dispatch': '2019-11-14',
      'time_of_dispatch': '6PM-8PM',
      'time_zone': 'Pacific Time',
    }
    dispatch_confirmed_note = lit_get_dispatch_confirmed_note(body)

    assert dispatch_confirmed_note == expected_dispatch_confirmed_note


expected_tech_12_hours_before_sms_note = """#*MetTel's IPA*# DIS37266
Dispatch 12h prior reminder SMS sent to +16666666666
"""


def lit_get_tech_12_hours_before_sms_note_test():
    body = {
        'dispatch_number': 'DIS37266',
        'phone_number': '+16666666666',
        'hours': '12'

    }
    tech_12_hours_before_sms_note = lit_get_tech_x_hours_before_sms_note(body)

    assert tech_12_hours_before_sms_note == expected_tech_12_hours_before_sms_note


expected_tech_2_hours_before_sms_note = """#*MetTel's IPA*# DIS37266
Dispatch 2h prior reminder SMS sent to +16666666666
"""


def lit_get_tech_2_hours_before_sms_note_test():
    body = {
        'dispatch_number': 'DIS37266',
        'phone_number': '+16666666666',
        'hours': '2'
    }
    tech_2_hours_before_sms_note = lit_get_tech_x_hours_before_sms_note(body)

    assert tech_2_hours_before_sms_note == expected_tech_2_hours_before_sms_note
