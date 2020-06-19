import iso8601
from pytz import timezone


def map_get_dispatch(body):
    '''
    From CTS to dispatch portal
    '''
    body = {k.lower(): v for k, v in body.items()}
    dispatch_request = {}
    # TODO: not implemented - map fields properly
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
        "location_address_2": body['job_site_street_2'],
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

    # Sandbox - creation fields
    if False:
        # "2007-01-25T12:00:00Z"
        final_datetime = f"{body['date_of_dispatch']}T{body['time_of_dispatch']}Z"
        final_time_zone = body('time_zone', '').replace(' Time', '')
        final_time_zone = timezone(f'US/{final_time_zone}')
        datetime_template = f"{body['date_of_dispatch']}T{body['time_of_dispatch']}:00"
        datetime_of_dispatch = iso8601.parse_date(datetime_template, final_time_zone)
        # TODO: parse datetime to string with format "2007-01-25T12:00:00Z"
        dispatch_request_test = {
            "early_start__c": datetime_of_dispatch,
            "local_site_time__c": datetime_of_dispatch,
            "ext_ref_num__c": body["mettel_bruin_ticket_id"],
            # "sla_level": body["sla_level"],
            "Location__c": "a1Y0n000000czUkEAI",
            "lookup_location_owner__c": body["job_site"],
            "country__c": body["location_country"],
            "state__c": body["job_site_state"],
            "street__c": f"{body['job_site_street_1']} {body['job_site_street_2']}",
            "zip__c": body["job_site_zip_code"],
            # "parent_account_associated__c": "Mettel",
            # "service_order__c": "a200n000000hKPSAA2",
            # "project_name__c": "Installations",
            "location__c": "a1Y0n000000czUkEAI",
            # "job_site_street": body["job_site_street"],
            # "job_site_city": body["job_site_city"],
            # "job_site_state": body["job_site_state"],
            # "job_site_zip_code": body["job_site_zip_code"],
            # "job_site_contact_name": body["job_site_contact_name"],
            # "job_site_contact_phone_number": body["job_site_contact_number"],
            "special_shipping_instructions__c": body["mettel_tech_call_in_instructions"],
            "service_type__c": "a250n000000P5N9AAK"
        }

    return dispatch_request
