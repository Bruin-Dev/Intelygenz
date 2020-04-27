export const dispatchLitInAdapter = data => ({
  // site_survey_quote_required, job_site_contact_name
  id: data.id,
  vendor: data.vendor,
  slaLevel: '===not set===',
  status: data.status || '===not set===',
  dateDispatch: data.dispatch.date_of_dispatch,
  mettelId: data.dispatch.dispatch_number,
  timeDispatch: data.dispatch.time_of_dispatch,
  timeZone: data.dispatch.time_zone,
  turnUp: data.dispatch.turn_up || '===not set===',
  hardTimeDispatch: data.dispatch.hardTimeDispatch || '===not set===',
  hardTimeZone: data.dispatch.hardTimeZone || '===not set===',
  requester: {
    name: data.dispatch.name_of_mettel_requester,
    groupEmail: data.dispatch.mettel_group_email || '===not set===',
    email: data.dispatch.mettel_requester_email,
    department: data.dispatch.mettel_department,
    phoneNumber: '===not set===',
    departmentPhoneNumber:
      data.dispatch.mettel_department_phone_number || '===not set==='
  },
  onSiteContact: {
    site: data.dispatch.job_site,
    street: data.dispatch.job_site_street,
    city: data.dispatch.job_site_city,
    state: data.dispatch.job_site_state,
    zip: data.dispatch.job_site_zip_code,
    phoneNumber: data.dispatch.job_site_contact_number
  },
  details: {
    serviceType: data.dispatch.scope_of_work,
    instructions: data.dispatch.mettel_tech_call_in_instructions,
    materials: data.dispatch.materials_needed_for_dispatch,
    information: '===not set===',
    specialMaterials: '===not set===',
    fieldEngineer:
      data.dispatch.field_engineer_name ||
      data.dispatch.field_engineer_last_name
        ? `${data.dispatch.field_engineer_name} ${data.dispatch.field_engineer_last_name}`
        : '===not set===',
    fieldEngineerContactNumber: data.dispatch.field_engineer_contact_number
  }
});

export const dispatchLitOutAdapter = data => ({
  date_of_dispatch: data.dateDispatch,
  site_survey_quote_required: false,
  time_of_dispatch: data.timeDispatch,
  time_zone: data.timeZone,
  mettel_bruin_ticket_id: data.mettelId,
  job_site: data.address1,
  job_site_street: data.address2,
  job_site_city: data.city,
  job_site_state: data.state,
  job_site_zip_code: data.zip,
  job_site_contact_name: `${data.firstName} ${data.lastName}`,
  job_site_contact_number: data.phoneNumberRequester,
  materials_needed_for_dispatch: data.materials,
  scope_of_work: data.issues,
  mettel_tech_call_in_instructions: data.instructions,
  name_of_mettel_requester: `${data.firstNameRequester} ${data.lastNameRequester}`,
  mettel_department: data.department,
  mettel_requester_email: data.emailRequester
  // slaLevel, vendor, phoneNumber, owner, email, serviceType
});
