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
