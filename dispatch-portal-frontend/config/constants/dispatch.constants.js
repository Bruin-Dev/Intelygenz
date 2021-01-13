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

export const slaLevelOptions = ['Pre-planned', 'Next bussiness day', 'Immediately'];

export const requesterPhoneNumberOptions = [
  {
    label: 'POTs Repair - (800) 856-0890',
    value: '8008560890'
  },
  { label: 'T1 Repair - (877) 515-0911', value: '8775150911' },
  { label: 'Wireless - (888) 638-2232', value: '8886382232' },
  {
    label: 'Advanced Services Implementations - (833) 864-6692',
    value: '8338646692'
  },
  {
    label: 'Akshay Shelar (646) 949-4591',
    value: '6469494591'
  },
  { label: 'Andy - (212) 607-2058', value: '2126072058' },
  {
    label: 'Beajan Mehrpour - (212) 359-5424',
    value: '2123595424'
  },
  { label: 'Bobby - (212) 607-2026', value: '2126072026' },
  {
    label: 'Brian Sullivan - (732) 837-9561',
    value: '7328379561'
  },
  {
    label: 'Bryant Espindola  - (212) 359-5129',
    value: '2123595129'
  },
  {
    label: 'Cameron Beeson - (385) 262-3442',
    value: '3852623442'
  },
  { label: 'Carmelita - (212) 359-0958', value: '2123590958' },
  { label: 'Daniel - (212) 607-2121', value: '2126072121' },
  {
    label: 'Dave Litvinsky - (866) 796-2259 X3',
    value: '8667962259'
  },
  {
    label: 'David Johnson - (212) 359-5371',
    value: '2123595371'
  },
  { label: 'Dennis - (212) 359-5303', value: '2123595303' },
  {
    label: 'Dennis Mcmahon - (212) 359-5349',
    value: '2123595349'
  },
  {
    label: 'George Chwang - (732) 837-9576',
    value: '7328379576'
  },
  {
    label: 'Gerardo Baez - (212) 359-5017',
    value: '2123595017'
  },
  {
    label: 'Heidi Carrero - (732) 444-7526',
    value: '7324447526'
  },
  {
    label: 'Holmdel NOC - (877) 520-6829',
    value: '8775206829'
  },
  { label: 'Jack Beck - (385) 262-3450', value: '3852623450' },
  {
    label: 'James Wood - (212) 607-2167',
    value: '2126072167'
  },
  {
    label: 'Jeremy Phillips - (212) 359-5321',
    value: '2123595321'
  },
  {
    label: 'Jonathan Pla - (646) 350-3956',
    value: '6463503956'
  },
  { label: 'Joseph - (212) 359-6361', value: '2123596361' },
  {
    label: 'Joseph DeGeorge - (732) 837-9568',
    value: '7328379568'
  },
  { label: 'Julie - (212) 359-5294', value: '2123595294' },
  {
    label: 'Justin Taylor - (732) 837-9567',
    value: '7328379567'
  },
  { label: 'Kelley - (212) 359-5325', value: '2123595325' },
  {
    label: 'Kia Robinson - (732) 837-9577',
    value: '7328379577'
  },
  {
    label: 'Kimberly Parker - (732) 837-9574',
    value: '7328379574'
  },
  {
    label: 'Luzmilda Cerda - (212) 607-2069',
    value: '2126072069'
  },
  {
    label: 'Margaret Sitima - (732) 837-9506',
    value: '7328379506'
  },
  {
    label: 'Matthew Gard - (732) 837-9571',
    value: '7328379571'
  },
  {
    label: 'Mayur Kenjale - (732) 837-9505',
    value: '7328379505'
  },
  {
    label: 'Meagan Abeltin - (212) 359-6399',
    value: '2123596399'
  },
  {
    label: 'Mike De Santo - 732-837-9578',
    value: '7328379578'
  },
  {
    label: 'Mindy Wright - (212) 359-5358',
    value: '2123595358'
  },
  {
    label: 'Nakul  Deshpande - (347) 277-9926',
    value: '3472779926'
  },
  {
    label: 'Nicholas Carter - (385) 262-3452',
    value: '3852623452'
  },
  {
    label: 'Nicholas DiMuro - (732) 837-9570',
    value: '7328379570'
  },
  {
    label: 'Nick Carter - (385) 262-3452',
    value: '3852623452'
  },
  {
    label: 'Pranav Kothawade - (385) 262-3426',
    value: '3852623426'
  },
  {
    label: 'Rekha Raju - (385) 262-3430',
    value: '3852623430'
  },
  { label: 'Ric Rean - (646) 665-1788', value: '6466651788' },
  {
    label: 'Robert Johnson - 732-837-9583',
    value: '7328379583'
  },
  {
    label: 'Robert Librizzi - (732) 837-9503',
    value: '7328379503'
  },
  {
    label: 'Robert Russo (212) 359-5331',
    value: '2123595331'
  },
  { label: 'Ronnie - (212) 607-2067', value: '2126072067' },
  {
    label: 'Sean Wilcox - (212) 359-0579',
    value: '2123590579'
  },
  { label: 'Sharmin - (212) 359-5106', value: '2123595106' },
  { label: 'Stacey - (212) 359-5091', value: '2123595091' },
  {
    label: 'Stephen Nitti - (732) 837-9521',
    value: '7328379521'
  },
  {
    label: 'Tom Barone - (646) 626-7651',
    value: '6466267651'
  },
  {
    label: 'Vincent Pisino - (732) 837-9573',
    value: '7328379573'
  },
  {
    label: 'Wilfredo Reyes - (385) 262-3443',
    value: '3852623443'
  },
  {
    label: 'Willard Bodie - (212) 359-0949',
    value: '2123590949'
  }
];

/*
*
 {
    label: 'Tom Barone - tbarone@mettel.net',
    value: 'Tom Barone - tbarone@mettel.net'
  },
  {
    label: 'Mike Murden - mmurden@mettel.net',
    value: 'Mike Murden - mmurden@mettel.net'
  },
*
* */
