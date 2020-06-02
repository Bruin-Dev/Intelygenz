import { mockLitSingleDispatch } from '../../services/mocks/mocks';

export default {
  userEmail: 'mettel@mettel.com',
  userPassword: '1234',
  dispatch: {
    // Data for create new dispatch
    date_of_dispatch: '2020-05-29',
    job_site: 'Jesus asjh',
    job_site_city: 'Las Rozas',
    job_site_contact_name: 'Jesus',
    job_site_contact_lastname: 'Jc Xo',
    job_site_contact_number: '+1 3846384563',
    job_site_state: 'Alabama',
    job_site_street: 'Av españa 40',
    job_site_street2: 'Minas 8',
    job_site_zip_code: '28231',
    materials_needed_for_dispatch: '.asdasd........',
    mettel_bruin_ticket_id: '4656262',
    mettel_department: 'Customer Care',
    mettel_department_phone_number: '3846384563',
    mettel_requester_email: 'jesus.javega@intelygenz.com',
    mettel_requester_phone_number: '+1 3846384563',
    mettel_tech_call_in_instructions: 'Nothing...',
    name_of_mettel_requester: 'James',
    last_name_of_mettel_requester: 'Kidman',
    scope_of_work: 'Issues .....',
    time_of_dispatch: '12.00AM',
    time_zone: 'Eastern Time',
    vendor: 'LIT',
    id: '123'
  },
  getDispatch: {
    ...mockLitSingleDispatch
  }
};
