export const dispatchAdapter = data => ({
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
