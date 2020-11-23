// NOTE: ORs are because we receive different API data: GET ONE and GET ALL
import { getTimeZoneShortName } from '../../config/constants/dispatch.constants';

export const dispatchCtsInAdapter = data => ({
  id: data.id || '',
  vendor: (data.vendor && data.vendor.toUpperCase()) || '',
  slaLevel: '',
  status: (data.dispatch && data.dispatch.status__c) || '',
  dateDispatch: data.dateDispatch,
  mettelId: (data.dispatch && data.dispatch.ext_ref_num__c) || '',
  timeDispatch: (data.dispatch && data.dispatch.open_date__c) || '',
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
    departmentPhoneNumber: 'See "Details" section for requester phone number'
  },
  onSiteContact: {
    site: (data.dispatch && data.dispatch.lookup_location_owner__c) || '',
    street: (data.dispatch && data.dispatch.street__c) || '',
    city: (data.dispatch && data.dispatch.city__c) || '',
    state: (data.dispatch && data.dispatch.country__c) || '',
    zip: (data.dispatch && data.dispatch.zip__c) || '',
    phoneNumber: (data.dispatch && data.dispatch.job_site_contact_number) || '',
    name: ''
  },
  details: {
    serviceType: '',
    instructions: '',
    materials: '',
    information: (data.dispatch && data.dispatch.issue_summary__c) || '',
    specialMaterials: '',
    fieldEngineer: '',
    fieldEngineerContactNumber: '',
    res: (data.dispatch && data.dispatch.description__c) || ''
  }
});

export const dispatchCtsOutAdapter = data => {
  const dataAux = {
    date_of_dispatch: data.dateDispatch,
    site_survey_quote_required: false,
    time_of_dispatch: data.timeDispatch,
    time_zone: data.timeZone,
    mettel_bruin_ticket_id: data.mettelId,
    job_site: data.owner,
    job_site_street_1: data.address1,
    job_site_city: data.city,
    job_site_state: data.state,
    job_site_zip_code: data.zip,
    job_site_contact_name: data.firstName,
    job_site_contact_lastname: data.lastName,
    job_site_contact_number: data.phoneNumber,
    materials_needed_for_dispatch: data.materials,
    scope_of_work: data.issues,
    mettel_tech_call_in_instructions: data.instructions,
    name_of_mettel_requester: data.firstNameRequester,
    lastname_of_mettel_requester: data.lastNameRequester,
    mettel_department: data.department,
    mettel_requester_email: data.emailRequester,
    mettel_department_phone_number: data.phoneNumberRequester,
    sla_level: data.slaLevel,
    location_country: data.country,
    service_type:
      data.serviceType && data.serviceType.length
        ? data.serviceType.join(' and ')
        : ''
  };

  if (data.address2 && data.address2.trim()) {
    dataAux.job_site_street_2 = data.address2.trim();
  }

  return dataAux;
};

export const dispatchCtsInAdapterGeAll = data => ({
  bruinTicketId: data.ext_ref_num__c || '',
  customerLocation: `${data.street__c} ${data.city__c} ${data.country__c} ${data.zip__c}`,
  vendor: (data.vendor && data.vendor.toUpperCase()) || '',
  vendorDispatchId: data.name || '',
  scheduledTime: data.date_of_dispatch || '',
  status: data.status__c || ''
});
