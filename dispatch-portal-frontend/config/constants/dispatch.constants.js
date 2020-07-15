import { config } from '../config';

export const timeZoneOptions = [
  { name: 'Eastern Time', shortName: 'ET' },
  { name: 'Pacific Time', shortName: 'PT' },
  { name: 'Mountain Time', shortName: 'MT' },
  { name: 'Central Time', shortName: 'CT' },
  { name: 'Hawaii Time', shortName: 'HT' },
  { name: 'Alaska Time', shortName: 'AT' }
];

export const getTimeZoneShortName = timeZone => {
  const shortName = timeZoneOptions.filter(
    timeZoneOption => timeZoneOption.name === timeZone
  );

  return shortName.length ? shortName[0].shortName : '';
};

export const departmentOptions = [
  'Customer Care',
  'DSL',
  'T1 Repair',
  'POTs Repair',
  'Provisioning',
  'Advanced Services Engineering',
  'Wireless',
  'Holmdel Network Engineering',
  'Advanced Services Implementations',
  'Other'
];

export const slaOptions = ['Pre-Planned', 'Next Business Day', '4-Hour'];
export const vendorsOptions = [
  { name: config.VENDORS.LIT, value: config.VENDORS.LIT },
  { name: config.VENDORS.CTS, value: config.VENDORS.CTS }
];

export const serviceTypesOptions = [
  { name: 'Troubleshoot', value: 'troubleshoot' },
  { name: 'Part Replacement', value: 'replacement' },
  { name: 'Cable Run', value: 'cable' }
];

export const timeOptions = [
  `12.00AM`,
  `12.30AM`,
  `1.00AM`,
  `1.30AM`,
  `2.00AM`,
  `2.30AM`,
  `3.00AM`,
  `3.30AM`,
  `4.00AM`,
  `4.30AM`,
  `5.00AM`,
  `5.30AM`,
  `6.00AM`,
  `6.30AM`,
  `7.00AM`,
  `7.30AM`,
  `8.00AM`,
  `8.30AM`,
  `9.00AM`,
  `9.30AM`,
  `10.00AM`,
  `10.30AM`,
  `11.00AM`,
  `11.30AM`,
  `12.00PM`,
  `12.30PM`,
  `1.00PM`,
  `1.30PM`,
  `2.00PM`,
  `2.30PM`,
  `3.00PM`,
  `3.30PM`,
  `4.00PM`,
  `4.30PM`,
  `5.00PM`,
  `5.30PM`,
  `6.00PM`,
  `6.30PM`,
  `7.00PM`,
  `7.30PM`,
  `8.00PM`,
  `8.30PM`,
  `9.00PM`,
  `9.30PM`,
  `10.00PM`,
  `10.30PM`,
  `11.00PM`,
  `11.30PM`
];

export const countryOptions = ['United States', 'Canada', 'PR'];

export const slaLevelOptions = ['Pre-planned', 'Next bussiness day'];

export const requesterPhoneNumberOptions = [
  'POTs Repair - (800) 856-0890',
  'T1 Repair - (877) 515-0911',
  'Wireless - (888) 638-2232',
  'Advanced Services Implementations - (833) 864-6692',
  'Akshay Shelar (646) 949-4591',
  'Andy - (212) 607-2058',
  'Beajan Mehrpour - (212) 359-5424',
  'Bobby - (212) 607-2026',
  'Brian Sullivan - (732) 837-9561',
  'Bryant Espindola  - (212) 359-5129',
  'Cameron Beeson - (385) 262-3442',
  'Carmelita - (212) 359-0958',
  'Daniel - (212) 607-2121',
  'Dave Litvinsky - (866) 796-2259 X3',
  'David Johnson - (212) 359-5371',
  'Dennis - (212) 359-5303',
  'Dennis Mcmahon - (212) 359-5349',
  'George Chwang - (732) 837-9576',
  'Gerardo Baez - (212) 359-5017',
  'Heidi Carrero - (732) 444-7526',
  'Holmdel NOC - (877) 520-6829',
  'Jack Beck - (385) 262-3450',
  'James Wood - (212) 607-2167',
  'Jeremy Phillips - (212) 359-5321',
  'Jonathan Pla - (646) 350-3956',
  'Joseph - (212) 359-6361',
  'Joseph DeGeorge - (732) 837-9568',
  'Julie - (212) 359-5294',
  'Justin Taylor - (732) 837-9567',
  'Kelley - (212) 359-5325',
  'Kia Robinson - (732) 837-9577',
  'Kimberly Parker - (732) 837-9574',
  'Luzmilda Cerda - (212) 607-2069',
  'Margaret Sitima - (732) 837-9506',
  'Matthew Gard - (732) 837-9571',
  'Mayur Kenjale - (732) 837-9505',
  'Meagan Abeltin - (212) 359-6399',
  'Mike De Santo - 732-837-9578',
  'Mike Murden - mmurden@mettel.net',
  'Mindy Wright - (212) 359-5358',
  'Nakul  Deshpande - (347) 277-9926',
  'Nicholas Carter - (385) 262-3452',
  'Nicholas DiMuro - (732) 837-9570',
  'Nick Carter - (385) 262-3452',
  'Pranav Kothawade - (385) 262-3426',
  'Rekha Raju - (385) 262-3430',
  'Ric Rean - (646) 665-1788',
  'Robert Johnson - 732-837-9583',
  'Robert Librizzi - (732) 837-9503',
  'Robert Russo (212) 359-5331',
  'Ronnie - (212) 607-2067',
  'Sean Wilcox - (212) 359-0579',
  'Sharmin - (212) 359-5106',
  'Stacey - (212) 359-5091',
  'Stephen Nitti - (732) 837-9521',
  'Tom Barone - (646) 626-7651',
  'Tom Barone - tbarone@mettel.net',
  'Vincent Pisino - (732) 837-9573',
  'Wilfredo Reyes - (385) 262-3443',
  'Willard Bodie - (212) 359-0949'
];
