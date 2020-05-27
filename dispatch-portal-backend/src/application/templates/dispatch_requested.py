LIT_DISPATCH_REQUESTED = """#*Automation Engine*#
Dispatch Management - Dispatch Requested

Please see the summary below.
--
Dispatch Number: {dispatch_number}
Date of Dispatch: {date_of_dispatch}
Time of Dispatch (Local): {time_of_dispatch}
Time Zone (Local): {time_zone}

Location Owner/Name: {job_site}
Address: {job_site_street}, {job_site_city}, {job_site_state}, {job_site_zip_code}
On-Site Contact: {job_site_contact_name}
Phone: {job_site_contact_number}

Issues Experienced:
{scope_of_work}
Arrival Instructions: {mettel_tech_call_in_instructions}
Materials Needed:
{materials_needed_for_dispatch}

Requester
Name: {name_of_mettel_requester}
Phone: {mettel_department_phone_number}
Email: {mettel_requester_email}
Department: {mettel_department}
"""


def get_clickable_link(name, url):
    return f'[{name}|{url}]'


def get_dispatch_requested_note(body, dispatch_number):
    link_to_dispatch = get_clickable_link(
        dispatch_number,
        f"https://master.mettel-automation.net/dispatch_portal/dispatch/{dispatch_number}"
    )
    return LIT_DISPATCH_REQUESTED.format(
        dispatch_number=link_to_dispatch,
        date_of_dispatch=body.get('date_of_dispatch'),
        time_of_dispatch=body.get('time_of_dispatch'),
        time_zone=body.get('time_zone'),
        job_site=body.get('job_site'),
        job_site_street=body.get('job_site_street'),
        job_site_city=body.get('job_site_city'),
        job_site_state=body.get('job_site_state'),
        job_site_zip_code=body.get('job_site_zip_code'),
        job_site_contact_name=body.get('job_site_contact_name'),
        job_site_contact_number=body.get('job_site_contact_number'),
        scope_of_work=body.get('scope_of_work'),
        mettel_tech_call_in_instructions=body.get('mettel_tech_call_in_instructions'),
        materials_needed_for_dispatch=body.get('materials_needed_for_dispatch'),
        name_of_mettel_requester=body.get('name_of_mettel_requester'),
        mettel_department_phone_number=body.get('mettel_department_phone_number'),
        mettel_requester_email=body.get('mettel_requester_email'),
        mettel_department=body.get('mettel_department')
    )
