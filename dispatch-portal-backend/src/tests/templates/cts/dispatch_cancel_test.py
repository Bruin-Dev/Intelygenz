from application.templates.cts.dispatch_cancel import get_dispatch_cancel_request_note

expected_dispatch_cancel_request_note = """#*MetTel's IPA*# S-12345
Dispatch Management - Dispatch Cancel Requested

A request to cancel the dispatch for 2019-11-14 05:30:00 PST has been sent.
"""


def get_dispatch_cancel_note_test():
    dispatch_number = 'S-12345'
    body = {
        'dispatch_number': dispatch_number,
        'date_of_dispatch': '2019-11-14 05:30:00 PST'
    }
    dispatch_cancel_request_note = get_dispatch_cancel_request_note(body, dispatch_number)

    assert dispatch_cancel_request_note == expected_dispatch_cancel_request_note
