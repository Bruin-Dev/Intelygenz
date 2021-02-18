from application.templates.lit.lit_repair_completed import lit_get_repair_completed_note

expected_repair_completed_note = """#*MetTel's IPA*# DIS37266
Dispatch Management - Repair Completed

Dispatch request for 2019-11-14 @ 6PM-8PM Pacific Time has been completed.
Reference: 4663397
"""


def get_repair_completed_note_test():
    body = {
        'dispatch_number': 'DIS37266',
        'date_of_dispatch': '2019-11-14',
        'time_of_dispatch': '6PM-8PM',
        'time_zone': 'Pacific Time',
        'ticket_id': '4663397'
    }
    repair_completed_note = lit_get_repair_completed_note(body)

    assert repair_completed_note == expected_repair_completed_note
