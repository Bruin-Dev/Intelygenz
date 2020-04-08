
"""
GET - Response
{
    "turn_up": "True",
    "time_zone_local": "Central Time",
    "time_of_check_out": null,
    "time_of_check_in": null,
    "tech_off_site": false,
    "tech_mobile_number": null,
    "tech_first_name": null,
    "tech_arrived_on_site": false,
    "special_materials_needed_for_dispatch": "6",
    "special_dispatch_notes": "test",
    "site_survey_quote_required": true,
    "scope_of_work": "test",
    "name_of_mettel_requester": "JC_TEST",
    "mettel_tech_call_in_instructions": "test",
    "mettel_requester_email": null,
    "mettel_note_updates": null,
    "mettel_group_email": "activations@mettel.net",
    "mettel_department_phone_number": "Bobby Santiago - (908) 876-5674",
    "mettel_department": "Advanced Services Engineering",
    "mettel_bruin_ticketid": "1",
    "local_time_of_dispatch": null,
    "job_site_zip_code": "10038-4201",
    "job_site_street": "test street",
    "job_site_state": "NY",
    "job_site_contact_name_and_phone_number": "Derek Fuentes 4154270954",
    "job_site_city": "New York",
    "job_site": "me test",
    "information_for_tech": null,
    "hard_time_of_dispatch_time_zone_local": null,
    "hard_time_of_dispatch_local": null,
    "dispatch_status": "New Dispatch",
    "dispatch_number": "DIS37423",
    "date_of_dispatch": "2020-04-16",
    "close_out_notes": null,
    "backup_mettel_department_phone_number": "Bobby Santiago - (212) 607-2121"
}
"""

"""
POST - Request to API
{
  "date_of_dispatch": "2019-11-14",
  "site_survey_quote_required": false,
  "time_of_dispatch": "6PM-8PM",
  "time_zone": "Pacific Time",
  "mettel_bruin_ticket_id": 0,
  "job_site": "Red Rose Inn",
  "job_site_street": "123 Fake Street",
  "job_site_city": "Pleasantown",
  "job_site_state": "CA",
  "job_site_zip_code": "99088",
  "job_site_contact_name": "Jane Doe",
  "job_site_contact_number": "+1 666 6666 666",
  "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
  "scope_of_work": "Device is bouncing constantly",
  "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
  "name_of_mettel_requester": "Karen Doe",
  "mettel_department": "Customer Care",
  "mettel_requester_email": "karen.doe@mettel.net"
}

// This actually works
{
  "date_of_dispatch": "2019-11-14",
  "site_survey_quote_required": false,
  "local_time_of_dispatch": "6PM-8PM",
  "time_zone_local": "Pacific Time",
  "job_site": "Red Rose Inn",
  "job_site_street": "123 Fake Street",
  "job_site_city": "Pleasantown",
  "job_site_state": "CA",
  "job_site_zip_code": "99088",
  "job_site_contact_name_and_phone_number": "Jane Doe +1 666 6666 666",
  "special_materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
  "scope_of_work": "Device is bouncing constantly",
  "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
  "name_of_mettel_requester": "Karen Doe",
  "mettel_department": "Customer Care",
  "mettel_requester_email": "karen.doe@mettel.net"
}

Map previous to RequestDispatch

{
  "RequestDispatch": {
    "date_of_dispatch": "2016-11-16",
    "site_survey_quote_required": false,
    "local_time_of_dispatch": "7AM-9AM",
    "time_zone_local": "Pacific Time",
    "turn_up": "Yes",
    "hard_time_of_dispatch_local": "7AM-9AM",
    "hard_time_of_dispatch_time_zone_local": "Eastern Time",
    "name_of_mettel_requester": "Test User1",
    "mettel_group_email": "test@mettel.net",
    "mettel_requester_email": "test@mettel.net",
    "mettel_department": "Customer Care",
    "mettel_department_phone_number": "1233211234",
    "backup_mettel_department_phone_number": "1233211234",
    "job_site": "test",
    "job_site_street": "test street",
    "job_site_city": "test city",
    "job_site_state": "test state2",
    "job_site_zip_code": "123321",
    "scope_of_work": "test",
    "mettel_tech_call_in_instructions": "test",
    "special_dispatch_notes": "Test Create No Special Dispatch Notes to Pass Forward",
    "job_site_contact_name_and_phone_number": "test",
    "information_for_tech": "test",
    "special_materials_needed_for_dispatch": "test"
  }
}

"""
