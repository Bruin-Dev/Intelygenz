LIT_DISPATCH_REQUESTED = """#*Automation Engine*#
Dispatch Management - Dispatch Confirmed
Dispatch scheduled by {vendor} for {date_of_dispatch} @ {time_of_dispatch} {am_pm} {time_zone}

Field Engineer
Larry Andershock
(310) 525-4183
"""


def lit_get_dispatch_confirmed_note(body):
    return LIT_DISPATCH_REQUESTED.format(
        vendor='LIT',
        date_of_dispatch=body.get('date_of_dispatch'),
        time_of_dispatch=body.get('time_of_dispatch'),
        am_pm=body.get('am_pm'),
        time_zone=body.get('time_zone')
    )
