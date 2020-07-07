export const mockLitSingleDispatch = {
  vendor: 'LIT',
  slaLevel: '3',
  id: 'DIS17918', // IMPORTANTE: debe coincidir con el del OBTENER DETALLE(el get), para que los test E2E funcionen correctamente
  dispatch: {
    date_of_dispatch: '2020-01-31',
    dispatch_number: 'DIS17918',
    dispatch_status: 'New Dispatch',
    job_site: 'test site',
    job_site_city: 'test job site city',
    job_site_contact_name: 'update Job',
    job_site_contact_number: '+34 7894864658',
    job_site_state: 'ALABAMA',
    job_site_street: 'test job site street',
    job_site_zip_code: '10041',
    materials_needed_for_dispatch: 'test',
    mettel_bruin_ticket_id: 'BRUINID5478525',
    mettel_department: 'T1 Repair',
    mettel_department_phone_number: '564894568689689',
    mettel_requester_phone_number: '5656456',
    mettel_requester_email: 'requester@mettel.net',
    mettel_tech_call_in_instructions: 'update callin instruction',
    name_of_mettel_requester: 'Test User1',
    scope_of_work: 'test new scope of work',
    site_survey_quote_required: false,
    time_of_dispatch: '7AM-9AM',
    time_zone: 'Pacific Time',
    hardTimeDispatch: '7AM-9AM',
    hardTimeZone: 'Pacific Time',
    field_engineer_name: 'JC',
    field_engineer_last_name: 'Jávega',
    field_engineer_contact_number: '+34633292080'
  }
};
