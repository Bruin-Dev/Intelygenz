import iso8601
from pytz import timezone


def map_get_dispatch(body, datetime_formatted):
    '''
    From CTS to dispatch portal
    '''
    body = {k.lower(): v for k, v in body.items()}
    dispatch_request = {}
    # TODO: not implemented - map fields properly
    body['date_of_dispatch'] = datetime_formatted
    body['date_of_dispatch'] = datetime_formatted
    return body


def map_create_dispatch(body):
    '''
    from dispatch portal to cts
    '''
    body = {k.lower(): v for k, v in body.items()}

    # month/day/year hh:mm
    # Email
    dispatch_request = {
        "onsite_time_needed": f"{body['date_of_dispatch']} {body['time_of_dispatch']}",
        "timezone_of_dispatch": body['time_zone'],
        "reference": body["mettel_bruin_ticket_id"],
        "sla_level": body["sla_level"],
        "location_country": body['location_country'],
        "location_owner": body["job_site"],
        "location_address_1": body['job_site_street_1'],
        "location_address_2": body.get('job_site_street_2', ''),
        "city": body["job_site_city"],
        "state": body["job_site_state"],
        "zip": body["job_site_zip_code"],
        "onsite_contact_name": body["job_site_contact_name"],
        "onsite_contact_lastname": body["job_site_contact_lastname"],
        "onsite_contact_phone_number": body["job_site_contact_number"],
        "failure_experienced": body["scope_of_work"],
        "materials_needed": body["materials_needed_for_dispatch"],
        "service_category": body["service_type"],
        "onsite_sow": body["mettel_tech_call_in_instructions"],
        "name": body["name_of_mettel_requester"],
        "lastname": body["lastname_of_mettel_requester"],
        "phone_number": body["mettel_department_phone_number"],
        "email": body["mettel_requester_email"],
        "mettel_department": body["mettel_department"]
    }

    return dispatch_request
