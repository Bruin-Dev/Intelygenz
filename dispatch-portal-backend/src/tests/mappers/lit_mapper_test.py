from application.mappers.lit_mapper import map_get_dispatch, map_create_dispatch, map_update_dispatch


class TestMappers:

    def map_get_dispatch_test(self):
        content = {
            "turn_up": None,
            "Time_Zone_Local": "Pacific Time",
            "Time_of_Check_Out": None,
            "Time_of_Check_In": None,
            "Tech_Off_Site": False,
            "Tech_Mobile_Number": None,
            "Tech_First_Name": None,
            "Tech_Arrived_On_Site": False,
            "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "Special_Dispatch_Notes": None,
            "Site_Survey_Quote_Required": False,
            "Scope_of_Work": "Device is bouncing constantly",
            "Name_of_MetTel_Requester": "Karen Doe",
            "MetTel_Tech_Call_In_Instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "MetTel_Requester_Email": "karen.doe@mettel.net",
            "MetTel_Note_Updates": None,
            "MetTel_Group_Email": None,
            "MetTel_Department_Phone_Number": '(111) 111-1111',
            "MetTel_Department": "Customer Care",
            "MetTel_Bruin_TicketID": "T-12345",
            "Local_Time_of_Dispatch": "5.30AM",
            "Job_Site_Zip_Code": "99088",
            "Job_Site_Street": "123 Fake Street",
            "Job_Site_State": "CA",
            "Job_Site_Contact_Name_and_Phone_Number": "Jane Doe +1 666 6666 666",
            "Job_Site_City": "Pleasantown",
            "Job_Site": "test street",
            "Information_for_Tech": None,
            "Hard_Time_of_Dispatch_Time_Zone_Local": "Pacific Time",
            "Hard_Time_of_Dispatch_Local": "5.30AM",
            "Dispatch_Status": "New Dispatch",
            "Dispatch_Number": "DIS37450",
            "Date_of_Dispatch": "2019-11-14",
            "Close_Out_Notes": None,
            "Backup_MetTel_Department_Phone_Number": None,
            "dispatch_status": "New Dispatch"
        }

        expected_map = {
            "dispatch_number": "DIS37450",
            "date_of_dispatch": "Nov 14, 2019 @ 12:30 AM Pacific",
            "site_survey_quote_required": False,
            "time_of_dispatch": "5.30AM",
            "time_zone": "Pacific Time",
            "hard_time_of_dispatch_local": "5.30AM",
            "hard_time_of_dispatch_time_zone_local": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "test street",
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
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_requester_phone_number": '(111) 111-1111',
            "dispatch_status": "New Dispatch",
            "dispatch_tech_name": None,
            "dispatch_tech_phone": None
        }
        datetime_formatted = 'Nov 14, 2019 @ 12:30 AM Pacific'

        assert expected_map == map_get_dispatch(content, datetime_formatted)

    def map_get_dispatch_contact_none_test(self):
        content = {
            "turn_up": None,
            "Time_Zone_Local": "Pacific Time",
            "Time_of_Check_Out": None,
            "Time_of_Check_In": None,
            "Tech_Off_Site": False,
            "Tech_Mobile_Number": None,
            "Tech_First_Name": None,
            "Tech_Arrived_On_Site": False,
            "Special_Materials_Needed_for_Dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "Special_Dispatch_Notes": None,
            "Site_Survey_Quote_Required": False,
            "Scope_of_Work": "Device is bouncing constantly",
            "Name_of_MetTel_Requester": "Karen Doe",
            "MetTel_Tech_Call_In_Instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "MetTel_Requester_Email": "karen.doe@mettel.net",
            "MetTel_Note_Updates": None,
            "MetTel_Group_Email": None,
            "MetTel_Department_Phone_Number": '(111) 111-1111',
            "MetTel_Department": "Customer Care",
            "MetTel_Bruin_TicketID": "T-12345",
            "Local_Time_of_Dispatch": "5.30AM",
            "Job_Site_Zip_Code": "99088",
            "Job_Site_Street": "123 Fake Street",
            "Job_Site_State": "CA",
            "Job_Site_Contact_Name_and_Phone_Number": None,
            "Job_Site_City": "Pleasantown",
            "Job_Site": "test street",
            "Information_for_Tech": None,
            "Hard_Time_of_Dispatch_Time_Zone_Local": "Pacific Time",
            "Hard_Time_of_Dispatch_Local": "5.30AM",
            "Dispatch_Status": "New Dispatch",
            "Dispatch_Number": "DIS37450",
            "Date_of_Dispatch": "2019-11-14",
            "Close_Out_Notes": None,
            "Backup_MetTel_Department_Phone_Number": None,
            "dispatch_status": "New Dispatch"
        }

        expected_map = {
            "dispatch_number": "DIS37450",
            "date_of_dispatch": "Nov 14, 2019 @ 12:30 AM Pacific",
            "site_survey_quote_required": False,
            "time_of_dispatch": "5.30AM",
            "time_zone": "Pacific Time",
            "hard_time_of_dispatch_local": "5.30AM",
            "hard_time_of_dispatch_time_zone_local": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
            "job_site": "test street",
            "job_site_street": "123 Fake Street",
            "job_site_city": "Pleasantown",
            "job_site_state": "CA",
            "job_site_zip_code": "99088",
            "job_site_contact_name": "",
            "job_site_contact_number": "",
            "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
            "scope_of_work": "Device is bouncing constantly",
            "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
            "name_of_mettel_requester": "Karen Doe",
            "mettel_department": "Customer Care",
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_requester_phone_number": '(111) 111-1111',
            "dispatch_status": "New Dispatch",
            "dispatch_tech_name": None,
            "dispatch_tech_phone": None
        }

        datetime_formatted = 'Nov 14, 2019 @ 12:30 AM Pacific'

        assert expected_map == map_get_dispatch(content, datetime_formatted)

    def map_create_dispatch_test(self):
        content = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
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
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "16666666666",
            "sla_level": "Pre-planned",
        }

        expected_map = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "6PM-8PM",
            "time_zone_local": "Pacific Time",
            "hard_time_of_dispatch_local": "6PM-8PM",
            "hard_time_of_dispatch_time_zone_local": "Pacific Time",
            "mettel_bruin_ticketid": "T-12345",
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
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "16666666666"
        }
        assert expected_map == map_create_dispatch(content)

    def map_create_dispatch_immediately_test(self):
        content = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "time_of_dispatch": "6PM-8PM",
            "time_zone": "Pacific Time",
            "mettel_bruin_ticket_id": "T-12345",
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
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "16666666666",
            "sla_level": "Immediately",
        }

        expected_map = {
            "date_of_dispatch": "2019-11-14",
            "site_survey_quote_required": False,
            "local_time_of_dispatch": "ASAP",
            "time_zone_local": "Pacific Time",
            "hard_time_of_dispatch_local": "6PM-8PM",
            "hard_time_of_dispatch_time_zone_local": "Pacific Time",
            "mettel_bruin_ticketid": "T-12345",
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
            "mettel_requester_email": "karen.doe@mettel.net",
            "mettel_department_phone_number": "16666666666"
        }
        assert expected_map == map_create_dispatch(content)

    def map_update_dispatch_test(self):
        content = {
            "date_of_dispatch": "2019-11-15"
        }

        expected_map = {
            "date_of_dispatch": "2019-11-15"
        }
        assert expected_map == map_update_dispatch(content)

    def map_update_dispatch_with_full_contact_test(self):
        content = {
            "date_of_dispatch": "2019-11-15",
            "job_site_contact_name": "Jane Doe",
            "job_site_contact_number": "+1 666 6666 666"
        }

        expected_map = {
            "date_of_dispatch": "2019-11-15",
            "job_site_contact_name_and_phone_number": "Jane Doe +1 666 6666 666",
        }
        assert expected_map == map_update_dispatch(content)

    def map_update_dispatch_without_full_contact_test(self):
        content = {
            "date_of_dispatch": "2019-11-15",
            "job_site_contact_name": "Jane Doe"
        }

        expected_map = {
            "date_of_dispatch": "2019-11-15"
        }
        assert expected_map == map_update_dispatch(content)
