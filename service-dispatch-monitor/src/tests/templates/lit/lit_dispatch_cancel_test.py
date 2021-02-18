from application.templates.lit.lit_dispatch_cancel import lit_get_dispatch_cancel_note


expected_dispatch_confirmed_note = """#*MetTel's IPA*# DIS12345
Dispatch Management - Dispatch Cancelled
Dispatch for 2019-11-14 @ 6PM-8PM Pacific Time has been cancelled.
"""


def lit_get_dispatch_cancel_note_test():
    body = {
        'dispatch_number': 'DIS12345',
        'date_of_dispatch': '2019-11-14 @ 6PM-8PM Pacific Time'
    }
    dispatch_cancel_note = lit_get_dispatch_cancel_note(body)

    assert dispatch_cancel_note == expected_dispatch_confirmed_note
