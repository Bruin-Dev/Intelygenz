CTS_DISPATCH_CANCEL = """#*Automation Engine*# {dispatch_number}
Dispatch Management - Dispatch Cancelled
Dispatch for {date_of_dispatch} has been cancelled.
"""


def cts_get_dispatch_cancel_note(body):
    return CTS_DISPATCH_CANCEL.format(
        dispatch_number=body.get('dispatch_number'),
        date_of_dispatch=body.get('date_of_dispatch')
    )
