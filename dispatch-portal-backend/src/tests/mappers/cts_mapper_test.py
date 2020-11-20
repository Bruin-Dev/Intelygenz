from application.mappers.cts_mapper import map_get_dispatch, map_create_dispatch


class TestMappers:

    def map_get_dispatch_test(self):
        requester_info = {
            'requester_name': 'Test Name',
            'requester_phone': '5102342333',
            'requester_email': 'man_test@gmail.com'
        }
        datetime_formatted = '2019-11-14 5.30AM'
        content = {
            'date_of_dispatch': "2019-11-14",
            'time_of_dispatch': "5.30AM",
            'time_zone': "Pacific",
            'mettel_bruin_ticket_id': '11111',
            'sla_level': None,
            'location_country': 'USA',
            'job_site': 99088,
            'job_site_street_1': '123 Fake Street',
            'job_site_City': 'Pleasantown',
            'job_site_state': 'CA',
            'job_site_zip_code': '99088',
            'job_Site_contact_name': "Jane Doe",
            'job_site_contact_lastname': 'Smith',
            'Job_site_contact_number': '+1 666 6666 666',
            'scope_of_work': 'Device is bouncing constantly',
            'materials_needed_for_dispatch': 'Laptop, cable, tuner, ladder,internet hotspot',
            'service_type': 'Test',
            'mettel_tech_call_in_instructions': 'When arriving to the site call HOLMDEL NOC for telematic assistance',
            'name_of_mettel_requester': 'Karen Doe',
            'lastname_of_mettel_requester': 'Yeap',
            'mettel_department_phone_number': '16666666666',
            'mettel_requester_email': 'karen.doe@mettel.net',
            'mettel_department': None,
            'igz_dispatch_number': '1234'
        }
        expected_result = {
            'date_of_dispatch': datetime_formatted,
            'time_of_dispatch': '5.30AM',
            'time_zone': 'Pacific',
            'mettel_bruin_ticket_id': '11111',
            'sla_level': None,
            'location_country': 'USA',
            'job_site': 99088,
            'job_site_street_1': '123 Fake Street',
            'job_site_city': 'Pleasantown',
            'job_site_state': 'CA',
            'job_site_zip_code': '99088',
            'job_site_contact_name': 'Jane Doe',
            'job_site_contact_lastname': 'Smith',
            'job_site_contact_number': '+1 666 6666 666',
            'scope_of_work': 'Device is bouncing constantly',
            'materials_needed_for_dispatch': 'Laptop, cable, tuner, ladder,internet hotspot',
            'service_type': 'Test',
            'mettel_tech_call_in_instructions': 'When arriving to the site call HOLMDEL NOC for telematic assistance',
            'name_of_mettel_requester': 'Karen Doe',
            'lastname_of_mettel_requester': 'Yeap',
            'mettel_department_phone_number': '16666666666',
            'mettel_requester_email': 'karen.doe@mettel.net',
            'mettel_department': None,
            'igz_dispatch_number': '1234',
            'requester_name': 'Test Name',
            'requester_phone': '5102342333',
            'requester_email': 'man_test@gmail.com'
        }

        result = map_get_dispatch(content, datetime_formatted, requester_info)
        assert result['date_of_dispatch'] == datetime_formatted
        assert result['requester_name'] == requester_info['requester_name']
        assert result['requester_phone'] == requester_info['requester_phone']
        assert result['requester_email'] == requester_info['requester_email']
        assert result == expected_result

    def map_create_dispatch_test(self):
        content = {
            'date_of_dispatch': "2019-11-14",
            'time_of_dispatch': "5.30AM",
            'time_zone': "Pacific",
            'mettel_bruin_ticket_id': '11111',
            'sla_level': None,
            'location_country': 'USA',
            'job_site': 99088,
            'job_site_street_1': '123 Fake Street',
            'job_site_City': 'Pleasantown',
            'job_site_state': 'CA',
            'job_site_zip_code': '99088',
            'job_Site_contact_name': "Jane Doe",
            'job_site_contact_lastname': 'Smith',
            'Job_site_contact_number': '+1 666 6666 666',
            'scope_of_work': 'Device is bouncing constantly',
            'materials_needed_for_dispatch': 'Laptop, cable, tuner, ladder,internet hotspot',
            'service_type': 'Test',
            'mettel_tech_call_in_instructions': 'When arriving to the site call HOLMDEL NOC for telematic assistance',
            'name_of_mettel_requester': 'Karen Doe',
            'lastname_of_mettel_requester': 'Yeap',
            'mettel_department_phone_number': '16666666666',
            'mettel_requester_email': 'karen.doe@mettel.net',
            'mettel_department': None,
            'igz_dispatch_number': '1234'
        }

        expected_map = {
            "onsite_time_needed": '2019-11-14 5.30AM',
            "timezone_of_dispatch": 'Pacific',
            "reference": '11111',
            "sla_level": None,
            "location_country": 'USA',
            "location_owner": 99088,
            "location_address_1": '123 Fake Street',
            "location_address_2": '',
            "city": 'Pleasantown',
            "state": 'CA',
            "zip": '99088',
            "onsite_contact_name": 'Jane Doe',
            "onsite_contact_lastname": 'Smith',
            "onsite_contact_phone_number": '+1 666 6666 666',
            "failure_experienced": 'Device is bouncing constantly',
            "materials_needed": 'Laptop, cable, tuner, ladder,internet hotspot',
            "service_category": 'Test',
            "onsite_sow": 'When arriving to the site call HOLMDEL NOC for telematic assistance',
            "name": 'Karen Doe',
            "lastname": 'Yeap',
            "phone_number": '16666666666',
            "email": 'karen.doe@mettel.net',
            "mettel_department": None,
            "igz_dispatch_number": '1234'
        }
        result = map_create_dispatch(content)
        assert expected_map == result
