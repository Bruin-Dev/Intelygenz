DISPATCH_REQUESTED = """#*Automation Engine*#
Dispatch Management - Dispatch Confirmed
Dispatch scheduled by {vendor} for {date_of_dispatch} @ {time_of_dispatch} {am_pm} {time_zone}
Dispatch scheduled by CTS for Mar 16, 2020 @ 07:00 AM Eastern.

Field Engineer
Larry Andershock
(310) 525-4183
"""


def get_dispatch_confirmed_note(body):
    return DISPATCH_REQUESTED.format(
        vendor='LIT',
        date_of_dispatch=body.get('date_of_dispatch'),
        time_of_dispatch=body.get('time_of_dispatch'),
        time_zone=body.get('time_zone'),
        sla_level=body.get('sla_level'),
        job_site=body.get('time_zone'),
        mettel_tech_call_in_instructions=body.get('mettel_tech_call_in_instructions'),
        name_of_mettel_requester=body.get('name_of_mettel_requester'),
        mettel_requester_phone_number=body.get('mettel_requester_phone_number'),
        mettel_requester_email=body.get('mettel_requester_email'),
        mettel_department=body.get('mettel_department')
    )
