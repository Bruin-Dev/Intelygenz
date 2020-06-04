export const mockLitSingleDispatch = {
  vendor: 'LIT',
  slaLevel: 3,
  id: 'DIS17918', // IMPORTANTE: debe coincidir con el del OBTENER DETALLE(el get), para que los test E2E funcionen correctamente
  status: 'completed',
  dispatch: {
    date_of_dispatch: '2016-11-16',
    dispatch_number: 'test update',
    time_of_dispatch: '7AM-9AM',
    time_zone: 'Pacific Time',
    turn_up: 'Yes',
    hardTimeDispatch: '7AM-9AM',
    hardTimeZone: 'Eastern Time',
    name_of_mettel_requester: 'Test User1',
    mettel_group_email: 'test@mettel.net',
    mettel_requester_email: 'test@mettel.net',
    mettel_department: 'Customer Care',
    mettel_department_phone_number: '1233211234',
    job_site: 'test',
    job_site_street: 'test street',
    job_site_city: 'test city',
    job_site_contact_number: 'test',
    job_site_state: 'test state2',
    job_site_zip_code: '123321',
    scope_of_work: 'test',
    mettel_tech_call_in_instructions: 'test',
    materials_needed_for_dispatch: 'test',
    specialMaterials: 'Test Create No Special Dispatch Notes to Pass Forward',
    information: 'test',
    field_engineer_name: 'JC',
    field_engineer_last_name: 'Jávega',
    field_engineer_contact_number: '+34633292080'
  }
};
