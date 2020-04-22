import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { config } from '../environments';

export const API_URLS = {
  LOGIN: '/api/login',
  DISPATCH: '/dispatch'
};

const baseConfig = {
  baseURL: config.baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
};

export const axiosInstance = axios.create(baseConfig);

// Mocks
const mock = new MockAdapter(axiosInstance, { delayResponse: 1000 });

mock.onPost(API_URLS.LOGIN).reply(200, {
  token: 'XXXX-fake-token'
});

mock.onGet(API_URLS.DISPATCH).reply(200, [
  {
    system: 'LIT',
    id: '001',
    customerLocation: 'Albacete Spain',
    bruinTicketId: '100221',
    timeScheduled: 'Mar 02, 2020 09:00 AM',
    status: 'requested'
  },
  {
    system: 'CTS',
    id: '002',
    customerLocation: 'OReilly Auto Parts',
    bruinTicketId: '200221',
    timeScheduled: 'Mar 03, 2020 11:00 AM',
    status: 'confirmed'
  },
  {
    system: 'CTS',
    id: '003',
    customerLocation: 'OReilly Auto Parts',
    bruinTicketId: '300221',
    timeScheduled: 'Mar 10, 2020 03:00 AM',
    status: 'in progress'
  },
  {
    system: 'LIT',
    id: '004',
    customerLocation: 'Albacete Spain',
    bruinTicketId: '400221',
    timeScheduled: 'Mar 14, 2020 10:00 AM',
    status: 'completed'
  },
  {
    system: 'CTS',
    id: '005',
    customerLocation: 'OReilly Auto Parts',
    bruinTicketId: '500221',
    timeScheduled: 'Mar 16, 2020 06:00 AM',
    status: 'completed'
  },
  {
    system: 'LIT',
    id: '006',
    customerLocation: 'Albacete Spain',
    bruinTicketId: '600221',
    timeScheduled: 'Mar 02, 2020 09:00 AM',
    status: 'requested'
  },
  {
    system: 'CTS',
    id: '007',
    customerLocation: 'OReilly Auto Parts',
    bruinTicketId: '700221',
    timeScheduled: 'Mar 03, 2020 11:00 AM',
    status: 'confirmed'
  },
  {
    system: 'CTS',
    id: '008',
    customerLocation: 'OReilly Auto Parts',
    bruinTicketId: '800221',
    timeScheduled: 'Mar 10, 2020 03:00 AM',
    status: 'in progress'
  },
  {
    system: 'LIT',
    id: '009',
    customerLocation: 'Albacete Spain',
    bruinTicketId: '900221',
    timeScheduled: 'Mar 14, 2020 10:00 AM',
    status: 'completed'
  },
  {
    system: 'CTS',
    id: '010',
    customerLocation: 'OReilly Auto Parts',
    bruinTicketId: '1000221',
    timeScheduled: 'Mar 16, 2020 06:00 AM',
    status: 'completed'
  },
  {
    system: 'CTS',
    id: '011',
    customerLocation: 'OReilly Auto Parts',
    bruinTicketId: '1100221',
    timeScheduled: 'Mar 16, 2020 06:00 AM',
    status: 'completed'
  }
]);

mock.onPost(API_URLS.DISPATCH).reply(204);

mock.onGet(new RegExp(`${API_URLS.DISPATCH}/*`)).reply(200, {
  vendor: 'LIT',
  slaLevel: 3,
  Dispatch_Number: 'DIS17918',
  Date_of_Dispatch: '2016-11-16',
  MetTel_Max_ID: 'test update',
  Local_Time_of_Dispatch: '7AM-9AM',
  Time_Zone_Local: 'Pacific Time',
  Turn_Up: 'Yes',
  Hard_Time_of_Dispatch_Local: '7AM-9AM',
  Hard_Time_of_Dispatch_Time_Zone_Local: 'Eastern Time',
  Name_of_MetTel_Requester: 'Test User1',
  MetTel_Group_Email: 'test@mettel.net',
  MetTel_Requester_Email: 'test@mettel.net',
  MetTel_Department: 'Customer Care',
  MetTel_Department_Phone_Number: '1233211234',
  Backup_MetTel_Department_Phone_Number: '1233211234',
  Job_Site: 'test',
  Job_Site_Street: 'test street',
  Job_Site_City: 'test city',
  Job_Site_State: 'test state2',
  Job_Site_Zip_Code: '123321',
  Scope_of_Work: 'test',
  MetTel_Tech_Call_In_Instructions: 'test',
  Special_Dispatch_Notes:
    'Test Create No Special Dispatch Notes to Pass Forward',
  Job_Site_Contact_Name_and_Phone_Number: 'test',
  Information_for_Tech: 'test',
  Special_Materials_Needed_for_Dispatch: 'test'
});
