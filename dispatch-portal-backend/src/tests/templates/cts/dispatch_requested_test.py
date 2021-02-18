from application.templates.cts.dispatch_requested import get_dispatch_requested_note

expected_dispatch_request_note = """#*MetTel's IPA*# IGZ_XXX
Dispatch Management - Dispatch Requested

Please see the summary below.
--
Dispatch Number: IGZ_XXX
Date of Dispatch: 2019-11-14
Time of Dispatch (Local): 6PM-8PM
Time Zone (Local): Pacific Time
SLA Level: Pre-planned

Location Owner/Name: Red Rose Inn
Address: 123 Fake Street, Pleasantown, CA, 99088
On-Site Contact: Jane Doe
Phone: +1 666 6666 666

Issues Experienced:
Device is bouncing constantly
Arrival Instructions: When arriving to the site call HOLMDEL NOC for telematic assistance
Materials Needed:
Laptop, cable, tuner, ladder,internet hotspot

Requester
Name: Karen Doe
Phone: +1 666 6666 666
Email: karen.doe@mettel.net
Department: Customer Care
"""


def get_dispatch_requested_note_test():
    dispatch_number = 'IGZ_XXX'
    body = {
        'date_of_dispatch': '2019-11-14',
        'site_survey_quote_required': False,
        'time_of_dispatch': '6PM-8PM',
        'time_zone': 'Pacific Time',
        'sla_level': 'Pre-planned',
        'mettel_bruin_ticket_id': '4656262',
        'job_site': 'Red Rose Inn',
        'job_site_street_1': '123 Fake Street',
        'job_site_city': 'Pleasantown',
        'job_site_state': 'CA',
        'job_site_zip_code': '99088',
        'job_site_contact_name': 'Jane Doe',
        'job_site_contact_number': '+1 666 6666 666',
        'materials_needed_for_dispatch': 'Laptop, cable, tuner, ladder,internet hotspot',
        'scope_of_work': 'Device is bouncing constantly',
        'mettel_tech_call_in_instructions': 'When arriving to the site call HOLMDEL NOC for telematic assistance',
        'name_of_mettel_requester': 'Karen Doe',
        'mettel_department': 'Customer Care',
        'mettel_requester_email': 'karen.doe@mettel.net',
        'mettel_department_phone_number': '+1 666 6666 666'
    }
    dispatch_request_note = get_dispatch_requested_note(body, dispatch_number)

    assert dispatch_request_note == expected_dispatch_request_note
