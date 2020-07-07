import { getTimeZoneShortName } from '../../config/constants/dispatch.constants';

export const dispatchLitInAdapter = data => ({
  id: data.id || '',
  vendor: (data.vendor && data.vendor.toUpperCase()) || '',
  slaLevel: data.slaLevel || '',
  status: (data.dispatch && data.dispatch.dispatch_status) || '',
  dateDispatch: (data.dispatch && data.dispatch.date_of_dispatch) || '',
  mettelId: (data.dispatch && data.dispatch.mettel_bruin_ticket_id) || '',
  timeDispatch: (data.dispatch && data.dispatch.time_of_dispatch) || '',
  timeZone: (data.dispatch && data.dispatch.time_zone) || '',
  turnUp: (data.dispatch && data.dispatch.turn_up) || '',
  hardTimeDispatch: (data.dispatch && data.dispatch.hardTimeDispatch) || '',
  hardTimeZone: (data.dispatch && data.dispatch.hardTimeZone) || '',
  requester: {
    name: (data.dispatch && data.dispatch.name_of_mettel_requester) || '',
    groupEmail: (data.dispatch && data.dispatch.mettel_group_email) || '',
    email: (data.dispatch && data.dispatch.mettel_requester_email) || '',
    department: (data.dispatch && data.dispatch.mettel_department) || '',
    phoneNumber:
      (data.dispatch && data.dispatch.mettel_requester_phone_number) || '',
    departmentPhoneNumber:
      (data.dispatch && data.dispatch.mettel_department_phone_number) || ''
  },
  onSiteContact: {
    site: (data.dispatch && data.dispatch.job_site) || '',
    street: (data.dispatch && data.dispatch.job_site_street) || '',
    city: (data.dispatch && data.dispatch.job_site_city) || '',
    state:
      (data.dispatch && data.dispatch.job_site_state) ||
      data.job_site_state ||
      '',
    zip: (data.dispatch && data.dispatch.job_site_zip_code) || '',
    phoneNumber: (data.dispatch && data.dispatch.job_site_contact_number) || '',
    name: (data.dispatch && data.dispatch.job_site_contact_name) || ''
  },
  details: {
    serviceType: '',
    instructions:
      (data.dispatch && data.dispatch.mettel_tech_call_in_instructions) || '',
    materials:
      (data.dispatch && data.dispatch.materials_needed_for_dispatch) || '',
    information: (data.dispatch && data.dispatch.scope_of_work) || '',
    specialMaterials: '',
    fieldEngineer:
      data.dispatch &&
      (data.dispatch.field_engineer_name ||
        data.dispatch.field_engineer_last_name)
        ? `${data.dispatch.field_engineer_name} ${data.dispatch.field_engineer_last_name}`
        : '',
    fieldEngineerContactNumber:
      (data.dispatch && data.dispatch.field_engineer_contact_number) || ''
  }
});

export const dispatchLitOutAdapter = data => ({
  date_of_dispatch: data.dateDispatch,
  site_survey_quote_required: false,
  time_of_dispatch: data.timeDispatch,
  time_zone: data.timeZone,
  mettel_bruin_ticket_id: data.mettelId,
  job_site: data.owner,
  job_site_street: `${data.address1} ${
    data.address2 && data.address2.trim() ? data.address2.trim() : ''
  }`,
  job_site_city: data.city,
  job_site_state: data.state,
  job_site_zip_code: data.zip,
  job_site_contact_name: `${data.firstName} ${data.lastName}`,
  job_site_contact_number: data.phoneNumber,
  materials_needed_for_dispatch: data.materials,
  scope_of_work: data.issues,
  mettel_tech_call_in_instructions: data.instructions,
  name_of_mettel_requester: `${data.firstNameRequester} ${data.lastNameRequester}`,
  mettel_department: data.department,
  mettel_requester_email: data.emailRequester,
  mettel_requester_phone_number: data.phoneNumberRequester,
  mettel_department_phone_number: data.phoneNumber
});

// Todo delete null and undefined
export const dispatchLitInAdapterGeAll = data => ({
  bruinTicketId: data.mettel_bruin_ticket_id || '',
  customerLocation: `${data.job_site_street} ${data.job_site_city} ${data.job_site_state} ${data.job_site_zip_code}`,
  vendor: (data.vendor && data.vendor.toUpperCase()) || '',
  vendorDispatchId: data.dispatch_number || '',
  scheduledTime: `${data.date_of_dispatch} ${
    data.time_of_dispatch
  } ${getTimeZoneShortName(data.time_zone)}`,
  status: data.dispatch_status || ''
});
