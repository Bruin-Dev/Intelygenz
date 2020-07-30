from application.templates.lit.lit_dispatch_cancel import lit_get_dispatch_cancel_note


expected_dispatch_confirmed_note = """#*Automation Engine*# DIS12345
Dispatch Management - Dispatch Cancelled
Dispatch for 2020-03-16 16:00:00 PDT has been cancelled.
"""


def lit_get_dispatch_cancel_note_test():
    body = {
        'dispatch_number': 'DIS12345',
        'date_of_dispatch': '2020-03-16 16:00:00 PDT'
    }
    dispatch_cancel_note = lit_get_dispatch_cancel_note(body)

    assert dispatch_cancel_note == expected_dispatch_confirmed_note
