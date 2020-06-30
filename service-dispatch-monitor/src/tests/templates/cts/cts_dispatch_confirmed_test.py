from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_dispatch_confirmed_sms_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_12_hours_before_sms_note
from application.templates.cts.cts_dispatch_confirmed import cts_get_tech_2_hours_before_sms_note

expected_dispatch_confirmed_note = """#*Automation Engine*#
Dispatch Management - Dispatch Confirmed
Dispatch scheduled for 2020-06-23T14:00:00.000+0000

Field Engineer
Michael J. Fox
+16666666666
"""


def cts_get_dispatch_requested_note_test():
    body = {
      'date_of_dispatch': '2020-06-23T14:00:00.000+0000',
      'tech_name': 'Michael J. Fox',
      'tech_phone': '+16666666666'
    }
    dispatch_confirmed_note = cts_get_dispatch_confirmed_note(body)

    assert dispatch_confirmed_note == expected_dispatch_confirmed_note


expected_cts_dispatch_confirmed_sms = """#*Automation Engine*#
Dispatch confirmation SMS sent to +16666666666
"""


def cts_get_confirmed_sms_note_test():
    body = {
        'phone_number': '+16666666666'
    }
    dispatch_confirmed_sms_note = cts_get_dispatch_confirmed_sms_note(body)

    assert dispatch_confirmed_sms_note == expected_cts_dispatch_confirmed_sms


expected_tech_12_hours_before_sms_note = """#*Automation Engine*#
Dispatch 12h prior reminder SMS sent to +16666666666
"""


def cts_get_tech_12_hours_before_sms_note_test():
    body = {
        'phone_number': '+16666666666'
    }
    tech_12_hours_before_sms_note = cts_get_tech_12_hours_before_sms_note(body)

    assert tech_12_hours_before_sms_note == expected_tech_12_hours_before_sms_note


expected_tech_2_hours_before_sms_note = """#*Automation Engine*#
Dispatch 2h prior reminder SMS sent to +16666666666
"""


def cts_get_tech_2_hours_before_sms_note_test():
    body = {
        'phone_number': '+16666666666'
    }
    tech_2_hours_before_sms_note = cts_get_tech_2_hours_before_sms_note(body)

    assert tech_2_hours_before_sms_note == expected_tech_2_hours_before_sms_note
