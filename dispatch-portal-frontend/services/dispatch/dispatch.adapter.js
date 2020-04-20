export const dispatchLitInAdapter = data => ({
  id: data.Dispatch_Number,
  vendor: data.vendor,
  slaLevel: data.slaLevel,
  dateDispatch: data.Date_of_Dispatch,
  mettelId: data.MetTel_Max_ID,
  timeDispatch: data.Local_Time_of_Dispatch,
  timeZone: data.Time_Zone_Local,
  turnUp: data.Turn_Up,
  hardTimeDispatch: data.Hard_Time_of_Dispatch_Local,
  hardTimeZone: data.Hard_Time_of_Dispatch_Time_Zone_Local,
  requester: {
    name: data.Name_of_MetTel_Requester,
    groupEmail: data.MetTel_Group_Email,
    email: data.MetTel_Requester_Email,
    department: data.MetTel_Department,
    phoneNumber: data.MetTel_Department_Phone_Number,
    departmentPhoneNumber: data.Backup_MetTel_Department_Phone_Number
  },
  onSiteContact: {
    site: data.Job_Site,
    street: data.Job_Site_Street,
    city: data.Job_Site_City,
    state: data.Job_Site_State,
    zip: data.Job_Site_Zip_Code,
    phoneNumber: data.Job_Site_Contact_Name_and_Phone_Number
  },
  details: {
    serviceType: data.Scope_of_Work,
    instructions: data.MetTel_Tech_Call_In_Instructions,
    materials: data.Special_Dispatch_Notes,
    information: data.Information_for_Tech,
    specialMaterials: data.Special_Materials_Needed_for_Dispatch
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
  scope_of_work: data.serviceType,
  mettel_tech_call_in_instructions: data.instructions,
  name_of_mettel_requester: `${data.firstNameRequester} ${data.lastNameRequester}`,
  mettel_department: data.department,
  mettel_requester_email: data.emailRequester
  // slaLevel, vendor, phoneNumber, owner, email, issues
});
