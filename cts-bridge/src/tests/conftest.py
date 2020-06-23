import copy
from unittest.mock import Mock

import pytest
from unittest import mock

from application.clients.cts_client import CtsClient
from application.repositories.cts_repository import CtsRepository

from asynctest import CoroutineMock

from config import testconfig


# Scopes
# - function
# - module
# - session

@pytest.fixture(scope='function')
def cts_client():
    logger = Mock()
    config = testconfig
    client = CtsClient(logger, config)
    return client


@pytest.fixture(scope='function')
def cts_repository(cts_client):
    # cts_client, logger, scheduler, config
    logger = Mock()
    scheduler = Mock()
    config = testconfig

    repository = CtsRepository(cts_client, logger, scheduler, config)
    return repository


@pytest.fixture(scope='function')
def dispatch_required_keys():
    dispatch_required_keys = ['date_of_dispatch', 'site_survey_quote_required', 'time_of_dispatch', 'time_zone',
                              'mettel_bruin_ticket_id', 'sla_level', 'location_country', 'job_site',
                              'job_site_street_1', 'job_site_street_2', 'job_site_city', 'job_site_state',
                              'job_site_zip_code', 'job_site_contact_name', 'job_site_contact_lastname',
                              'job_site_contact_number', 'materials_needed_for_dispatch', 'scope_of_work',
                              'mettel_tech_call_in_instructions', 'service_type', 'name_of_mettel_requester',
                              'lastname_of_mettel_requester', 'mettel_department', 'mettel_requester_email',
                              'mettel_department_phone_number']
    return dispatch_required_keys


@pytest.fixture(scope='function')
def new_dispatch():
    return {
        "date_of_dispatch": "2019-11-14",
        "site_survey_quote_required": False,
        "time_of_dispatch": "6PM-8PM",
        "time_zone": "Pacific Time",
        "mettel_bruin_ticket_id": "123456",
        "sla_level": "Pre-planned",
        "location_country": "United States",
        "job_site": "Red Rose Inn",
        "job_site_street_1": "123 Fake Street",
        "job_site_street_2": "123 Fake Street",
        "job_site_city": "Pleasantown",
        "job_site_state": "CA",
        "job_site_zip_code": "99088",
        "job_site_contact_name": "Jane",
        "job_site_contact_lastname": "Doe",
        "job_site_contact_number": "+1 666 6666 666",
        "materials_needed_for_dispatch": "Laptop, cable, tuner, ladder,internet hotspot",
        "scope_of_work": "Device is bouncing constantly",
        "mettel_tech_call_in_instructions": "When arriving to the site call HOLMDEL NOC for telematic assistance",
        "service_type": "Troubleshooting",
        "name_of_mettel_requester": "Karen",
        "lastname_of_mettel_requester": "Doe",
        "mettel_department": "Customer Care",
        "mettel_requester_email": "karen.doe@mettel.net",
        "mettel_department_phone_number": "+1 666 6666 666"
    }
