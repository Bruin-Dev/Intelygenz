// NOTE: ORs are because we receive different API data: GET ONE and GET ALL
export const dispatchLitInAdapter = data => ({
  // site_survey_quote_required, job_site_contact_name, hard_time_of_dispatch_local, hard_time_of_dispatch_time_zone_local
  id: data.id || data.dispatch_number || '===not set===',
  vendor: data.vendor || '===not set===',
  slaLevel: '===not set===',
  status:
    (data.dispatch && data.dispatch.dispatch_status) ||
    data.dispatch_status ||
    '===not set===',
  dateDispatch:
    (data.dispatch && data.dispatch.date_of_dispatch) ||
    data.date_of_dispatch ||
    '===not set===',
  mettelId:
    (data.dispatch && data.dispatch.dispatch_number) ||
    data.mettel_bruin_ticket_id ||
    '===not set===',
  timeDispatch:
    (data.dispatch && data.dispatch.time_of_dispatch) ||
    data.time_of_dispatch ||
    '===not set===',
  timeZone:
    (data.dispatch && data.dispatch.time_zone) ||
    data.time_zone ||
    '===not set===',
  turnUp: (data.dispatch && data.dispatch.turn_up) || '===not set===',
  hardTimeDispatch:
    (data.dispatch && data.dispatch.hardTimeDispatch) || '===not set===',
  hardTimeZone:
    (data.dispatch && data.dispatch.hardTimeZone) || '===not set===',
  requester: {
    name:
      (data.dispatch && data.dispatch.name_of_mettel_requester) ||
      data.name_of_mettel_requester ||
      '===not set===',
    groupEmail:
      (data.dispatch && data.dispatch.mettel_group_email) || '===not set===',
    email:
      (data.dispatch && data.dispatch.mettel_requester_email) ||
      data.mettel_requester_email ||
      '===not set===',
    department:
      (data.dispatch && data.dispatch.mettel_department) ||
      data.mettel_department ||
      '===not set===',
    phoneNumber: '===not set===',
    departmentPhoneNumber:
      (data.dispatch && data.dispatch.mettel_department_phone_number) ||
      '===not set==='
  },
  onSiteContact: {
    site:
      (data.dispatch && data.dispatch.job_site) ||
      data.job_site ||
      '===not set===',
    street:
      (data.dispatch && data.dispatch.job_site_street) ||
      data.job_site_street ||
      '===not set===',
    city:
      (data.dispatch && data.dispatch.job_site_city) ||
      data.job_site_city ||
      '===not set===',
    state:
      (data.dispatch && data.dispatch.job_site_state) ||
      data.job_site_state ||
      '===not set===',
    zip:
      (data.dispatch && data.dispatch.job_site_zip_code) ||
      data.job_site_zip_code ||
      '===not set===',
    phoneNumber:
      (data.dispatch && data.dispatch.job_site_contact_number) ||
      data.job_site_contact_number ||
      '===not set===',
    name:
      (data.dispatch && data.dispatch.job_site_contact_name) ||
      data.job_site_contact_name ||
      '===not set==='
  },
  details: {
    serviceType: '===not set===',
    instructions:
      (data.dispatch && data.dispatch.mettel_tech_call_in_instructions) ||
      data.mettel_tech_call_in_instructions ||
      '===not set===',
    materials:
      (data.dispatch && data.dispatch.materials_needed_for_dispatch) ||
      data.materials_needed_for_dispatch ||
      '===not set===',
    information:
      (data.dispatch && data.dispatch.scope_of_work) ||
      data.scope_of_work ||
      '===not set===',
    specialMaterials: '===not set===',
    fieldEngineer:
      data.dispatch &&
      (data.dispatch.field_engineer_name ||
        data.dispatch.field_engineer_last_name)
        ? `${data.dispatch.field_engineer_name} ${data.dispatch.field_engineer_last_name}`
        : '===not set===',
    fieldEngineerContactNumber:
      (data.dispatch && data.dispatch.field_engineer_contact_number) ||
      '===not set==='
  }
});

export const dispatchLitOutAdapter = data => ({
  date_of_dispatch: data.dateDispatch,
  site_survey_quote_required: false,
  time_of_dispatch: data.timeDispatch,
  time_zone: data.timeZone,
  mettel_bruin_ticket_id: data.mettelId,
  job_site: data.owner,
  job_site_street: `${data.address1} ${data.address2}`,
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
  // Only CTS: serviceType, slaLevel, email(site contact)
});
