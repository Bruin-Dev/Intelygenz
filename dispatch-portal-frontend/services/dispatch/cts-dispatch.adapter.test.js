import {
  dispatchCtsInAdapter,
  dispatchCtsInAdapterGeAll,
  dispatchCtsOutAdapter
} from './cts-dispatch.adapter';

import { dispatchCtsList } from '../mocks/data/cts/list-dispatch.mock';
import {
  ctsDispatchMockGetAll,
  ctsDispatchMockGetOne
} from '../mocks/data/cts/result-adapter-in-dispatch.datatest';
import { mockCtsSingleDispatch } from '../mocks/data/cts/single-dispatch.mock';
import { config } from '../../config/config';

describe('cts dispatch adapter tests', () => {
  it('check dispatchCtsInAdapter for get(single item)', () => {
    expect(dispatchCtsInAdapter(mockCtsSingleDispatch)).toMatchObject(
      ctsDispatchMockGetOne
    );
  });

  it('check dispatchCtsInAdapter for get(single item) without data', () => {
    expect(dispatchCtsInAdapter({})).toMatchObject({
      id: '',
      vendor: '',
      slaLevel: '',
      status: '',
      dateDispatch: undefined,
      mettelId: '',
      timeDispatch: '',
      timeZone: '',
      turnUp: '',
      hardTimeDispatch: '',
      hardTimeZone: '',
      requester: {
        name: 'See "Details" section for requester name',
        groupEmail: '',
        email: 'See "Details" section for requester email',
        department: '',
        phoneNumber: 'See "Details" section for requester phone number',
        departmentPhoneNumber:
          'See "Details" section for requester phone number'
      },
      onSiteContact: {
        site: '',
        street: '',
        city: '',
        state: '',
        zip: '',
        phoneNumber: '',
        name: ''
      },
      details: {
        serviceType: '',
        instructions: '',
        materials: '',
        information: '',
        specialMaterials: '',
        fieldEngineer: '',
        fieldEngineerContactNumber: '',
        res: ''
      }
    });
  });

  it('check dispatchCtsInAdapter for getAll', () => {
    expect(
      dispatchCtsInAdapterGeAll({
        ...dispatchCtsList.data[0],
        vendor: config.VENDORS.CTS
      })
    ).toMatchObject(ctsDispatchMockGetAll);
  });

  it('check dispatchCtsOutAdapter', () => {
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
      phoneNumber: '+6262626262626',
      materials: 'KSAD KDFM...',
      issues: 'adasdas ddas.....',
      instructions: '2332322333 sd adasd...',
      firstNameRequester: 'JC Dan',
      lastNameRequester: 'Daniels',
      department: 'None',
      emailRequester: 'sdga@example.com',
      phoneNumberRequester: '+6262626262626',
      serviceType: ['T1 service'],
      slaLevel: '9',
      country: 'Canada'
    };
    const mocksOutAdapterDispatch = {
      date_of_dispatch: '2020-05-29',
      job_site: 'JResus asjh',
      job_site_city: 'Las Rozas',
      job_site_contact_name: 'Julia',
      job_site_contact_lastname: 'Sanches',
      job_site_contact_number: '+6262626262626',
      job_site_state: 'Albacete',
      job_site_street_1: 'Av España',
      job_site_street_2: '36 a1',
      job_site_zip_code: '28231',
      materials_needed_for_dispatch: 'KSAD KDFM...',
      mettel_bruin_ticket_id: '123',
      mettel_department: 'None',
      mettel_requester_email: 'sdga@example.com',
      mettel_tech_call_in_instructions: '2332322333 sd adasd...',
      name_of_mettel_requester: 'JC Dan',
      lastname_of_mettel_requester: 'Daniels',
      scope_of_work: 'adasdas ddas.....',
      site_survey_quote_required: false,
      time_of_dispatch: '12.00AM',
      time_zone: 'Eastern Time',
      sla_level: '9',
      location_country: 'Canada',
      service_type: 'T1 service'
    };

    expect(dispatchCtsOutAdapter(formData)).toMatchObject(
      mocksOutAdapterDispatch
    );
  });
});
