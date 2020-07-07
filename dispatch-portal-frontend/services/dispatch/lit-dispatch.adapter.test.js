import {
  dispatchLitInAdapter,
  dispatchLitInAdapterGeAll,
  dispatchLitOutAdapter
} from './lit-dispatch.adapter';
import { mockLitSingleDispatch } from '../mocks/data/lit/single-dispatch.mock';
import {
  mocksInAdapterLitAllDispatchResult,
  mocksInAdapterLitSingleDispatchResult
} from '../mocks/data/lit/result-adapter-in-dispatch.datatest';
import { dispatchLitList } from '../mocks/data/lit/list-dispatch.mock';
import { config } from '../../config/config';

describe('lit dispatch adapter tests', () => {
  it('check dispatchLitInAdapter for get(single item)', () => {
    expect(dispatchLitInAdapter(mockLitSingleDispatch)).toMatchObject(
      mocksInAdapterLitSingleDispatchResult
    );
  });

  it('check dispatchLitInAdapter for get(single item) without data', () => {
    expect(dispatchLitInAdapter({})).toMatchObject({
      dateDispatch: '',
      details: {
        fieldEngineer: '',
        fieldEngineerContactNumber: '',
        information: '',
        instructions: '',
        materials: '',
        serviceType: '',
        specialMaterials: ''
      },
      hardTimeDispatch: '',
      hardTimeZone: '',
      id: '',
      mettelId: '',
      onSiteContact: {
        city: '',
        name: '',
        phoneNumber: '',
        site: '',
        state: '',
        street: '',
        zip: ''
      },
      requester: {
        department: '',
        departmentPhoneNumber: '',
        email: '',
        groupEmail: '',
        name: '',
        phoneNumber: ''
      },
      slaLevel: '',
      status: '',
      timeDispatch: '',
      timeZone: '',
      vendor: ''
    });
  });

  it('check dispatchLitInAdapter for getAll', () => {
    expect(
      dispatchLitInAdapterGeAll({
        ...dispatchLitList.data[0],
        vendor: config.VENDORS.LIT
      })
    ).toMatchObject(mocksInAdapterLitAllDispatchResult);
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
