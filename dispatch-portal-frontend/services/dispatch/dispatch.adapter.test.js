import {
  dispatchLitInAdapter,
  dispatchLitOutAdapter
} from './dispatch.adapter';
import { mockLitSingleDispatch } from '../mocks/single-dispatch.mock';
import { mocksInAdapterLitSingleDispatchResult } from '../mocks/new-dispatch.mock';

describe('dispatch adapter tests', () => {
  it('check dispatchLitInAdapter', () => {
    expect(dispatchLitInAdapter(mockLitSingleDispatch)).toMatchObject(
      mocksInAdapterLitSingleDispatchResult
    );
  });

  it('check dispatchLitOutAdapter', () => {
    const formData = {
      dateDispatch: '2020-05-29',
      timeDispatch: '12.00AM',
      timeZone: 'Eastern Time',
      mettelId: '123',
      owner: 'JResus asjh',
      address1: 'Av España',
      address2: '36 a1',
      city: 'Las Rozas',
      state: 'Albacete',
      zip: '28231',
      firstName: 'Julia',
      lastName: 'Sanches',
      phoneNumber: '+372357',
      materials: 'KSAD KDFM...',
      issues: 'adasdas ddas.....',
      instructions: '2332322333 sd adasd...',
      firstNameRequester: 'JC Dan',
      lastNameRequester: 'Daniels',
      department: 'None',
      emailRequester: 'sdga@example.com',
      phoneNumberRequester: '+6262626262626'
    };
    const mocksOutAdapterDispatch = {
      date_of_dispatch: '2020-05-29',
      job_site: 'JResus asjh',
      job_site_city: 'Las Rozas',
      job_site_contact_name: 'Julia Sanches',
      job_site_contact_number: '+372357',
      job_site_state: 'Albacete',
      job_site_street: 'Av España 36 a1',
      job_site_zip_code: '28231',
      materials_needed_for_dispatch: 'KSAD KDFM...',
      mettel_bruin_ticket_id: '123',
      mettel_department: 'None',
      mettel_department_phone_number: '+372357',
      mettel_requester_email: 'sdga@example.com',
      mettel_requester_phone_number: '+6262626262626',
      mettel_tech_call_in_instructions: '2332322333 sd adasd...',
      name_of_mettel_requester: 'JC Dan Daniels',
      scope_of_work: 'adasdas ddas.....',
      site_survey_quote_required: false,
      time_of_dispatch: '12.00AM',
      time_zone: 'Eastern Time'
    };

    expect(dispatchLitOutAdapter(formData)).toMatchObject(
      mocksOutAdapterDispatch
    );
  });
});
