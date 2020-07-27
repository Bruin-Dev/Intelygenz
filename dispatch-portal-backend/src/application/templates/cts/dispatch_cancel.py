CTS_DISPATCH_CANCEL_REQUEST = """#*Automation Engine*# {dispatch_number}
Dispatch Management - Dispatch Cancel Requested

A request to cancel the dispatch for {date_of_dispatch} has been sent.
"""


def get_dispatch_cancel_request_note(body, dispatch_number):
    return CTS_DISPATCH_CANCEL_REQUEST.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        dispatch_number=dispatch_number
    )
