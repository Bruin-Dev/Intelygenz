import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { API_URLS, baseConfig } from '../api';

export const axiosInstanceMocks = axios.create(baseConfig);

// Mocks

const mock = new MockAdapter(axiosInstanceMocks, { delayResponse: 1000 });

mock.onPost(API_URLS.LOGIN).reply(200, {
  token: 'XXXX-fake-token'
});

mock.onGet(API_URLS.DISPATCH).reply(200, [
  {
    vendor: 'lit',
    list_dispatch: [
      {
        dispatch_number: 'DIS37263',
        date_of_dispatch: '2015-01-01',
        site_survey_quote_required: true,
        time_of_dispatch: null,
        mettel_bruin_ticket_id: '0',
        time_zone: '2',
        job_site: 'Primary Citiscape',
        job_site_street: '124 Spring street',
        job_site_city: 'Citizville',
        job_site_state: 'NY',
        job_site_zip_code: '12345',
        job_site_contact_name: 'Rajat 11111',
        job_site_contact_number: '',
        materials_needed_for_dispatch: '1',
        scope_of_work: 'ScopeOfWork',
        mettel_tech_call_in_instructions: '1',
        name_of_mettel_requester: 'pkamath',
        mettel_department: '1',
        mettel_requester_email: 'pkamath@mettel.net',
        dispatch_status: 'New Dispatch'
      },
      {
        dispatch_number: 'DIS37266',
        date_of_dispatch: '2015-01-01',
        site_survey_quote_required: true,
        time_of_dispatch: null,
        mettel_bruin_ticket_id: '0|IW22800205',
        time_zone: 'Eastern Time',
        job_site: 'me test',
        job_site_street: '124 Spring street test',
        job_site_city: 'Citizville',
        job_site_state: 'NY',
        job_site_zip_code: '12345',
        job_site_contact_name: 'Rajat 1111111111',
        job_site_contact_number: '',
        materials_needed_for_dispatch:
          'Cat5E Patch cord(Roughly 3ft) or able to make one',
        scope_of_work: 'ScopeOfWork Test 123',
        mettel_tech_call_in_instructions: '456',
        name_of_mettel_requester: 'Pallavi Kamath',
        mettel_department: 'Advanced Services Implementations',
        mettel_requester_email: 'pkamath@mettel.net',
        dispatch_status: 'New Dispatch'
      },
      {
        dispatch_number: 'DIS37264',
        date_of_dispatch: '2015-01-01',
        site_survey_quote_required: true,
        time_of_dispatch: null,
        mettel_bruin_ticket_id: '0',
        time_zone: '2',
        job_site: 'Primary Citiscape',
        job_site_street: '124 Spring street',
        job_site_city: 'Citizville',
        job_site_state: 'NY',
        job_site_zip_code: '12345',
        job_site_contact_name: 'Rajat 11111',
        job_site_contact_number: '',
        materials_needed_for_dispatch: '1',
        scope_of_work: 'ScopeOfWork',
        mettel_tech_call_in_instructions: '1',
        name_of_mettel_requester: 'pkamath',
        mettel_department: '1',
        mettel_requester_email: 'pkamath@mettel.net',
        dispatch_status: 'New Dispatch'
      },
      {
        dispatch_number: 'DIS37265',
        date_of_dispatch: '2015-01-01',
        site_survey_quote_required: true,
        time_of_dispatch: null,
        mettel_bruin_ticket_id: '0',
        time_zone: '2',
        job_site: 'Primary Citiscape',
        job_site_street: '124 Spring street',
        job_site_city: 'Citizville',
        job_site_state: 'NY',
        job_site_zip_code: '12345',
        job_site_contact_name: 'Rajat 11111',
        job_site_contact_number: '',
        materials_needed_for_dispatch: '1',
        scope_of_work: 'ScopeOfWork',
        mettel_tech_call_in_instructions: '1',
        name_of_mettel_requester: 'pkamath',
        mettel_department: '1',
        mettel_requester_email: 'pkamath@mettel.net',
        dispatch_status: 'New Dispatch'
      },
      {
        dispatch_number: 'DIS37243',
        date_of_dispatch: '2016-11-16',
        site_survey_quote_required: false,
        time_of_dispatch: null,
        mettel_bruin_ticket_id: 'test update',
        time_zone: 'Pacific Time',
        job_site: 'test',
        job_site_street: 'test street',
        job_site_city: 'test city',
        job_site_state: 'test state2',
        job_site_zip_code: '123321',
        job_site_contact_name: 'test',
        job_site_contact_number: '',
        materials_needed_for_dispatch: 'test',
        scope_of_work: 'test',
        mettel_tech_call_in_instructions: 'test',
        name_of_mettel_requester: 'Test User1',
        mettel_department: 'Customer Care',
        mettel_requester_email: 'test@mettel.net',
        dispatch_status: 'New Dispatch'
      },
      {
        dispatch_number: 'DIS37466',
        date_of_dispatch: '2016-11-16',
        site_survey_quote_required: false,
        time_of_dispatch: null,
        mettel_bruin_ticket_id: null,
        time_zone: 'Pacific Time',
        job_site: 'Red Rose Inn',
        job_site_street: '123 Fake Street',
        job_site_city: 'Pleasantown',
        job_site_state: 'CA',
        job_site_zip_code: '99088',
        job_site_contact_name: 'Jane Doe',
        job_site_contact_number: '+1 666 6666 666',
        materials_needed_for_dispatch:
          'Laptop, cable, tuner, ladder,internet hotspot',
        scope_of_work: 'Device is bouncing constantly',
        mettel_tech_call_in_instructions:
          'When arriving to the site call HOLMDEL NOC for telematic assistance',
        name_of_mettel_requester: 'Karen Doe',
        mettel_department: 'Customer Care',
        mettel_requester_email: 'karen.doe@mettel.net',
        dispatch_status: 'New Dispatch'
      },
      {
        dispatch_number: 'DIS37286',
        date_of_dispatch: '2016-11-16',
        site_survey_quote_required: false,
        time_of_dispatch: null,
        mettel_bruin_ticket_id: null,
        time_zone: 'Pacific Time',
        job_site: 'test',
        job_site_street: 'test street',
        job_site_city: 'test city',
        job_site_state: 'test state2',
        job_site_zip_code: '123321',
        job_site_contact_name: 'test',
        job_site_contact_number: '',
        materials_needed_for_dispatch: 'test',
        scope_of_work: 'test',
        mettel_tech_call_in_instructions: 'test',
        name_of_mettel_requester: 'Test User1',
        mettel_department: 'Customer Care',
        mettel_requester_email: 'test@mettel.net',
        dispatch_status: 'New Dispatch'
      },
      {
        dispatch_number: 'DIS37366',
        date_of_dispatch: '2016-11-16',
        site_survey_quote_required: false,
        time_of_dispatch: null,
        mettel_bruin_ticket_id: null,
        time_zone: 'Pacific Time',
        job_site: 'test',
        job_site_street: null,
        job_site_city: 'test city',
        job_site_state: 'test state2',
        job_site_zip_code: '123321',
        job_site_contact_name: 'test',
        job_site_contact_number: '',
        materials_needed_for_dispatch: 'test',
        scope_of_work: 'test',
        mettel_tech_call_in_instructions: 'test',
        name_of_mettel_requester: 'Test User1',
        mettel_department: 'Customer Care',
        mettel_requester_email: 'test@mettel.net',
        dispatch_status: 'New Dispatch'
      },
      {
        dispatch_number: 'DIS37358',
        date_of_dispatch: '2016-11-16',
        site_survey_quote_required: false,
        time_of_dispatch: null,
        mettel_bruin_ticket_id: null,
        time_zone: 'Pacific Time',
        job_site: 'test',
        job_site_street: null,
        job_site_city: 'test city',
        job_site_state: 'test state2',
        job_site_zip_code: '123321',
        job_site_contact_name: 'test',
        job_site_contact_number: '',
        materials_needed_for_dispatch: 'test',
        scope_of_work: 'test',
        mettel_tech_call_in_instructions: 'test',
        name_of_mettel_requester: 'Test User1',
        mettel_department: 'Customer Care',
        mettel_requester_email: 'test@mettel.net',
        dispatch_status: 'New Dispatch'
      }
    ]
  }
]);

mock.onPost(API_URLS.DISPATCH).reply(204, { id: 123 });

mock.onPost(API_URLS.UPLOAD_FILES).reply(204);

mock.onGet(new RegExp(`${API_URLS.DISPATCH}/*`)).reply(200, {
  vendor: 'CTS',
  slaLevel: 3,
  id: 'DIS17918',
  status: 'completed',
  dispatch: {
    date_of_dispatch: '2016-11-16',
    dispatch_number: 'test update',
    time_of_dispatch: '7AM-9AM',
    time_zone: 'Pacific Time',
    turn_up: 'Yes',
    hardTimeDispatch: '7AM-9AM',
    hardTimeZone: 'Eastern Time',
    name_of_mettel_requester: 'Test User1',
    mettel_group_email: 'test@mettel.net',
    mettel_requester_email: 'test@mettel.net',
    mettel_department: 'Customer Care',
    mettel_department_phone_number: '1233211234',
    job_site: 'test',
    job_site_street: 'test street',
    job_site_city: 'test city',
    job_site_contact_number: 'test',
    job_site_state: 'test state2',
    job_site_zip_code: '123321',
    scope_of_work: 'test',
    mettel_tech_call_in_instructions: 'test',
    materials_needed_for_dispatch: 'test',
    specialMaterials: 'Test Create No Special Dispatch Notes to Pass Forward',
    information: 'test',
    field_engineer_name: 'JC',
    field_engineer_last_name: 'Jávega',
    field_engineer_contact_number: '+34633292080'
  }
});
