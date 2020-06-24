// NOTE: ORs are because we receive different API data: GET ONE and GET ALL
export const dispatchCtsInAdapter = data => ({
  id: data.name || data.id || '',
  vendor: (data.vendor && data.vendor.toUpperCase()) || '',
  slaLevel: data.slaLevel || '',
  status: (data.dispatch && data.dispatch.status__c) || data.status__c || '',
  dateDispatch:
    (data.dispatch && data.dispatch.date_of_dispatch) ||
    data.date_of_dispatch ||
    '',
  mettelId:
    (data.dispatch && data.dispatch.ext_ref_num__c) ||
    data.ext_ref_num__c ||
    '',
  timeDispatch:
    (data.dispatch && data.dispatch.open_date__c) || data.open_date__c || '',
  timeZone: (data.dispatch && data.dispatch.time_zone) || data.time_zone || '',
  turnUp: (data.dispatch && data.dispatch.turn_up) || '',
  hardTimeDispatch:
    (data.dispatch && data.dispatch.hardTimeDispatch) ||
    data.hardTimeDispatch ||
    '',
  hardTimeZone:
    (data.dispatch && data.dispatch.hardTimeZone) || data.hardTimeZone || '',
  requester: {
    name:
      (data.dispatch && data.dispatch.resource_email__c) ||
      data.resource_email__c ||
      '',
    groupEmail: (data.dispatch && data.dispatch.mettel_group_email) || '',
    email:
      (data.dispatch && data.dispatch.resource_email__c) ||
      data.resource_email__c ||
      '',
    department:
      (data.dispatch && data.dispatch.mettel_department) ||
      data.mettel_department ||
      '',
    phoneNumber:
      (data.dispatch && data.dispatch.resource_phone_number__c) ||
      data.resource_phone_number__c ||
      '',
    departmentPhoneNumber:
      (data.dispatch && data.dispatch.resource_phone_number__c) ||
      data.resource_phone_number__c ||
      ''
  },
  onSiteContact: {
    site:
      (data.dispatch && data.dispatch.lookup_location_owner__c) ||
      data.lookup_location_owner__c ||
      '',
    street: (data.dispatch && data.dispatch.street__c) || data.street__c || '',
    city: (data.dispatch && data.dispatch.city__c) || data.city__c || '',
    state: (data.dispatch && data.dispatch.country__c) || data.country__c || '',
    zip: (data.dispatch && data.dispatch.zip__c) || data.zip__c || '',
    phoneNumber:
      (data.dispatch && data.dispatch.job_site_contact_number) ||
      data.job_site_contact_number ||
      '',
    name:
      (data.dispatch && data.dispatch.job_site_contact_name) ||
      data.job_site_contact_name ||
      ''
  },
  details: {
    serviceType: '',
    instructions:
      (data.dispatch && data.dispatch.mettel_tech_call_in_instructions) ||
      data.mettel_tech_call_in_instructions ||
      '',
    materials:
      (data.dispatch && data.dispatch.materials_needed_for_dispatch) ||
      data.materials_needed_for_dispatch ||
      '',
    information:
      (data.dispatch && data.dispatch.issue_summary__c) ||
      data.issue_summary__c ||
      '',
    specialMaterials: '',
    fieldEngineer:
      data.dispatch &&
      (data.dispatch.field_engineer_name ||
        data.dispatch.field_engineer_last_name)
        ? `${data.dispatch.field_engineer_name} ${data.dispatch.field_engineer_last_name}`
        : '',
    fieldEngineerContactNumber:
      (data.dispatch && data.dispatch.field_engineer_contact_number) || '',
    res: data.description__c || data.dispatch.description__c || ''
  }
});

export const dispatchCtsOutAdapter = data => ({
  date_of_dispatch: data.dateDispatch,
  site_survey_quote_required: false,
  time_of_dispatch: data.timeDispatch,
  time_zone: data.timeZone,
  mettel_bruin_ticket_id: data.mettelId,
  job_site: data.owner,
  job_site_street_1: data.address1,
  job_site_street_2: data.address2,
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
});
