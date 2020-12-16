export const ctsDispatchMockGetOne = {
  id: 'S-151959',
  vendor: 'CTS',
  slaLevel: '',
  status: 'Completed',
  dateDispatch: undefined,
  mettelId: '4694961',
  timeDispatch: '2020-06-22T20:14:00.000+0000',
  timeZone: '',
  turnUp: '',
  hardTimeDispatch: '',
  hardTimeZone: '',
  requester: {
    name: 'Brad Gunnell',
    groupEmail: '',
    email: 't1repair@mettel.net',
    department: '',
    phoneNumber: '(877) 515-0911',
    departmentPhoneNumber: '(877) 515-0911'
  },
  onSiteContact: {
    site: 'Premier Financial Bancorp',
    street: '1501 K St NW',
    city: 'Washington',
    state: 'United States',
    zip: '20005',
    phoneNumber: '',
    name: ''
  },
  details: {
    serviceType: '',
    instructions: '',
    materials: '',
    information: 'Troubleshoot Modem/Check Cabling',
    specialMaterials: '',
    fieldEngineer: '',
    fieldEngineerContactNumber: '',
    res:
      "Onsite Time Needed: Jun 22, 2020 03:00 PM\r\n\r\nReference: 4694961\r\n\r\nSLA Level: 4-Hour\r\n\r\nLocation Country: United States\r\n\r\nLocation - US: 1501 K St NW\r\nWashington, DC 20005\r\n\r\nLocation ID: 88377\r\n\r\nLocation Owner: Premier Financial Bancorp\r\n\r\nOnsite Contact: Manager On Duty\r\n\r\nContact #: (202) 772-3610\r\n\r\nFailure Experienced: Comcast cable internet circuit is down. Comcast shows the modem offline without cause.\r\nBasic troubleshooting already done including power cycling of the VCE and modem. Client added it's showing red led on the VCE cloud.\r\nNeed to check the cabling and check out the Velo device and see if it needs replaced.\r\n\r\nStatic IP Address 50.211.140.109\r\nStatic IP Block 50.211.140.108/30\r\nGateway IP 50.211.140.110\r\nSubnet Mask 255.255.255.252\r\nPrimary DNS 75.75.75.75\r\nSecondary DNS 75.75.76.76\r\n\r\n\r\nOnsite SOW: phone # 877-515-0911 and email address for pictures to be sent to T1repair@mettel.net\r\n\r\nLCON: Mgr on Duty\r\nPhone: (202) 772-3610\r\nAcccess: M-F 9AM-5PM\r\n\r\nMaterials Needed: Laptop, Ethernet cable, console cable, Jetpack/Mobile Hotspot, TeamViewer installed, other IW tools (CAT5e, punch down, wall jacks, telecom standard toolkit)\r\n\r\nService Category: Troubleshoot\r\n\r\nName: Brad Gunnell\r\n\r\nPhone: (877) 515-0911\r\n\r\nEmail: t1repair@mettel.net"
  },
  fieldEngineer: {
    name: 'Geppert, Nicholas',
    phoneNumber: '(443) 340-7157'
  }
};

// Expect or result
export const ctsDispatchMockGetAll = {
  bruinTicketId: '4694961',
  customerLocation: '1501 K St NW Washington United States 20005',
  vendor: 'CTS',
  vendorDispatchId: 'S-151959',
  scheduledTime: '',
  status: 'Completed'
};
