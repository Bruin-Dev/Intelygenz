LIT_DISPATCH_REPAIR_COMPLETED = """*#Automation Engine#*
Dispatch Management - Repair Completed

Dispatch request for {date_of_dispatch} @ {time_of_dispatch} {am_pm} {time_zone} Eastern has been completed.
Reference: {ticket_id}
"""


def lit_get_repair_completed_note(body):
    return LIT_DISPATCH_REPAIR_COMPLETED.format(
        date_of_dispatch=body.get('date_of_dispatch'),
        time_of_dispatch=body.get('time_of_dispatch'),
        am_pm=body.get('am_pm'),
        time_zone=body.get('time_zone'),
        ticket_id=body.get('ticket_id')
    )
