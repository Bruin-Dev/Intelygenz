def map_get_dispatch(body):
    '''
    From CTS to dispatch portal
    '''
    body = {k.lower(): v for k, v in body.items()}
    dispatch_request = {}
    # raise Exception("TODO: not implemented")
    return body


def map_create_dispatch(body):
    '''
    from dispatch portal to cts
    '''
    body = {k.lower(): v for k, v in body.items()}
    dispatch_request = {
        "datetime_of_dispatch": f"{body['date_of_dispatch']} {body['time_of_dispatch']}",
        "timezone_of_dispatch": body['time_zone'],
        "reference": str(body["mettel_bruin_ticket_id"]),
        "sla_level": body["sla_level"],
        "job_country": "United States",  # TODO: Canada, ¿PR?
        "job_site": body["job_site"],  # Location Owner
        "job_site_street": body["job_site_street"],
        "job_site_city": body["job_site_city"],
        "job_site_state": body["job_site_state"],
        "job_site_zip_code": body["job_site_zip_code"],
        "job_site_contact_name": body["job_site_contact_name"],
        "job_site_contact_phone_number": body["job_site_contact_number"],
        "scope_of_work": body["scope_of_work"],  # TODO: Onsite SOW
        "failure_experienced": body["failure_experienced"],
        "special_materials_needed_for_dispatch": body["materials_needed_for_dispatch"],
        "mettel_tech_call_in_instructions": body["mettel_tech_call_in_instructions"],
        "services_categories": body["services_categories"],  # TODO: services_categories
        "mettel_department": body["mettel_department"],
        "name_of_mettel_requester": body["name_of_mettel_requester"],
        "mettel_department_phone_number": body["mettel_department_phone_number"],
        "mettel_requester_email": body["mettel_requester_email"],
        #######################################################
        "date_of_dispatch": body['date_of_dispatch'],

        "field52361222M": "month",
        "field52361222D": "day",
        "field52361222Y": "year",
        "field52361222H": "hour",
        "field52361222I": "minute",
        "field52361222A": "am_pm",

        "field52362094": "SLA LEVEL",

        "site_survey_quote_required": body['site_survey_quote_required'],

        "local_time_of_dispatch": body['time_of_dispatch'],

        "time_zone_local": body['time_zone'],
        "field74407345": "",

        # "job_site": body["job_site"],

        # "job_site_street": body["job_site_street"],
        "field52362051-address": "",
        "field52362051-address2": "",

        # "job_site_city": body["job_site_city"],
        "field52362051-city": "",

        # "job_site_state": body["job_site_state"],
        "field52362051-state": "",

        # "job_site_zip_code": body["job_site_zip_code"],
        "field52362051-zip": "",

        "field52361914": "location_id_field",
        "field52361998": "location_owner_field",

        "job_site_contact_name_and_phone_number": f'{body["job_site_contact_name"]} '
                                                  f'{body["job_site_contact_number"]}',
        "field52377770-first": "onsite_contact_first_name_field",
        "field52377770-last": "onsite_contact_last_name_field",
        "field52377777": "onsite_contact_phone_number_field",

        "field52380329": "failure_experienced_field",
        "field52380353": "onsite_sow_field",

        # "special_materials_needed_for_dispatch": body["materials_needed_for_dispatch"],
        "field56596157": "",

        # "scope_of_work": body["scope_of_work"],
        "field52380918": "services_categories",

        # "mettel_tech_call_in_instructions": body["mettel_tech_call_in_instructions"],

        "name_of_mettel_requester": body["name_of_mettel_requester"],
        "field52381072-first": "mettel_requester_name_field",
        "field52381072-last": "mettel_requester_last_name_field",

        "mettel_department": body["mettel_department"],

        "field52381073": "mettel_requester_phone_number_field",

        "mettel_requester_email": body["mettel_requester_email"],
        "field52381073": "mettel_requester_email_field",

        "field52361160": str(body["mettel_bruin_ticket_id"]),

        # Attachments
        # "field52381089": "attachment_1_field",
        # "field52381118": "attachment_2_field"
    }
    return dispatch_request
