def map_get_dispatch(body):
    '''
    From lit to dispatch portal
    '''
    body = {k.lower(): v for k, v in body.items()}
    dispatch_request = {
        "dispatch_number": body['dispatch_number'],
        "date_of_dispatch": body['date_of_dispatch'],
        "site_survey_quote_required": body['site_survey_quote_required'],
        "time_of_dispatch": body['local_time_of_dispatch'],
        "mettel_bruin_ticket_id": body["mettel_bruin_ticketid"],
        "time_zone": body['time_zone_local'],
        "job_site": body["job_site"],
        "job_site_street": body["job_site_street"],
        "job_site_city": body["job_site_city"],
        "job_site_state": body["job_site_state"],
        "job_site_zip_code": body["job_site_zip_code"],
        "job_site_contact_name": ' '.join(body['job_site_contact_name_and_phone_number'].split(' ')[:2]),
        "job_site_contact_number": ' '.join(body['job_site_contact_name_and_phone_number'].split(' ')[2:]),
        "materials_needed_for_dispatch": body["special_materials_needed_for_dispatch"],
        "scope_of_work": body["scope_of_work"],
        "mettel_tech_call_in_instructions": body["mettel_tech_call_in_instructions"],
        "name_of_mettel_requester": body["name_of_mettel_requester"],
        "mettel_department": body["mettel_department"],
        "mettel_requester_email": body["mettel_requester_email"],
        "dispatch_status": body['dispatch_status'],
    }
    return dispatch_request


def map_create_dispatch(body):
    '''
    from dispatch portal to lit
    '''
    body = {k.lower(): v for k, v in body.items()}
    dispatch_request = {
        "date_of_dispatch": body['date_of_dispatch'],
        "site_survey_quote_required": body['site_survey_quote_required'],
        "local_time_of_dispatch": body['time_of_dispatch'],
        "time_zone_local": body['time_zone'],
        "mettel_bruin_ticketid": body["mettel_bruin_ticket_id"],
        "job_site": body["job_site"],
        "job_site_street": body["job_site_street"],
        "job_site_city": body["job_site_city"],
        "job_site_state": body["job_site_state"],
        "job_site_zip_code": body["job_site_zip_code"],
        "job_site_contact_name_and_phone_number": f'{body["job_site_contact_name"]} '
                                                  f'{body["job_site_contact_number"]}',
        "special_materials_needed_for_dispatch": body["materials_needed_for_dispatch"],
        "scope_of_work": body["scope_of_work"],
        "mettel_tech_call_in_instructions": body["mettel_tech_call_in_instructions"],
        "name_of_mettel_requester": body["name_of_mettel_requester"],
        "mettel_department": body["mettel_department"],
        "mettel_requester_email": body["mettel_requester_email"],
    }
    return dispatch_request


def map_update_dispatch(body):
    '''
    from dispatch portal to lit
    '''
    body = {k.lower(): v for k, v in body.items()}

    dispatch_request = {
        "dispatch_number": body.get('dispatch_number', None),
        "date_of_dispatch": body.get('date_of_dispatch', None),
        "site_survey_quote_required": body.get('site_survey_quote_required', None),
        "local_time_of_dispatch": body.get('time_of_dispatch', None),
        "time_zone_local": body.get('time_zone', None),
        "mettel_bruin_ticketid": body.get("mettel_bruin_ticket_id", None),
        "job_site": body.get("job_site", None),
        "job_site_street": body.get("job_site_street", None),
        "job_site_city": body.get("job_site_city", None),
        "job_site_state": body.get("job_site_state", None),
        "job_site_zip_code": body.get("job_site_zip_code", None),
        "special_materials_needed_for_dispatch": body.get("materials_needed_for_dispatch", None),
        "scope_of_work": body.get("scope_of_work", None),
        "mettel_tech_call_in_instructions": body.get("mettel_tech_call_in_instructions", None),
        "name_of_mettel_requester": body.get("name_of_mettel_requester", None),
        "mettel_department": body.get("mettel_department", None),
        "mettel_requester_email": body.get("mettel_requester_email", None),
    }

    if "job_site_contact_name" in body and "job_site_contact_number" in body:
        dispatch_request["job_site_contact_name_and_phone_number"] =\
            f'{body["job_site_contact_name"]} {body["job_site_contact_number"]}'

    # Delete None keys
    dispatch_request = {k: v for k, v in dispatch_request.items() if v is not None}

    return dispatch_request
