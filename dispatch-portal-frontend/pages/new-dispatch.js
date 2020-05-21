import PropTypes from 'prop-types';
import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useForm } from 'react-hook-form';
import { privateRoute } from '../components/privateRoute/PrivateRoute';
import Menu from '../components/menu/Menu';
import Loading from '../components/loading/Loading';
import { dispatchService } from '../services/dispatch/dispatch.service';
import { Routes } from '../config/routes';
import { states } from '../config/constants/states';
import './new-dispatch.scss';
import { config } from '../config/config';

// Todo: refactor constant
const timeZoneOptions = [
  'Eastern Time',
  'Pacific Time',
  'Mountain Time',
  'Central Time',
  'Hawaii Time',
  'Alaska Time'
];

const departmentOptions = [
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

const slaOptions = ['Pre-Planned', 'Next Business Day', '4-Hour'];
const vendorsOptions = [
  // Todo: review
  { name: config.VENDORS.LIT, value: config.VENDORS.LIT },
  { name: config.VENDORS.CTS, value: config.VENDORS.CTS }
];
const serviceTypesOptions = [
  { name: 'Troubleshoot', value: 'troubleshoot' },
  { name: 'Part Replacement', value: 'replacement' },
  { name: 'Cable Run', value: 'cable' }
];

const timeOptions = [
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

function NewDispatch({ authToken }) {
  const router = useRouter();
  const { register, handleSubmit, errors } = useForm();
  const [response, setResponse] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [files, setFiles] = useState([]);
  const [selectedVendor, setSelectedVendor] = useState([]); // Note: ['CTS'] ['LIT'] ['CTS', 'LIT']

  const deleteFile = async index => {
    const auxArraySlice = [...files]; // For react state
    auxArraySlice.splice(index, 1);
    setFiles(auxArraySlice);
  };

  const onChangeHandlerFiles = async e => {
    e.preventDefault();
    setFiles([...files, ...e.target.files]);
  };

  const uploadFiles = async dispatchId => {
    const data = new FormData();
    files.map((file, index) => data.append('file', files[index]));

    const res = await dispatchService.uploadFiles(dispatchId, data);
    return res;
  };

  const onSubmit = async data => {
    setIsLoading(true);

    const res = await dispatchService.newDispatch(data);
    if (res && !res.error && res.data && res.data.id) {
      // Upload files
      // const resFiles = await uploadFiles(res.data.id);
      // if (resFiles) {
      // Go to details
      router.push(`${Routes.DISPATCH()}/${res.data.id}`);
      return;
      // }
    }
    // Todo: show/add upload error
    setResponse(res);
    setIsLoading(false);
  };

  const changeVendor = event => {
    const index = selectedVendor.indexOf(event.target.value);
    if (index > -1) {
      const auxSelectedVendors = [...selectedVendor];
      auxSelectedVendors.splice(index, 1);
      setSelectedVendor(auxSelectedVendors);
    } else {
      setSelectedVendor([...selectedVendor, event.target.value]);
    }
  };

  const showFieldByVendor = vendor => selectedVendor.includes(vendor);

  return (
    <>
      <Menu authToken={authToken} />
      <div className="new-dispatch-wrapper">
        <p className="form-title">New Dispatch Request</p>
        <form
          onSubmit={handleSubmit(onSubmit)}
          className="max-w-full rounded shadow-lg"
        >
          <div className="brick">
            <label htmlFor="dateDispatch">
              Date of dispatch <br />
              <input
                type="date"
                name="dateDispatch"
                id="dateDispatch"
                ref={register({ required: true })}
                className={errors.dateDispatch && 'error'}
              />
              {errors.dateDispatch && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="timeDispatch">
              Time of dispatch (Local)
              <br />
              <select
                name="timeDispatch"
                id="timeDispatch"
                ref={register({ required: true })}
                className={errors.timeDispatch && 'error'}
              >
                {timeOptions.map(time => (
                  <option value={time} key={`time-${time}`}>
                    {time}
                  </option>
                ))}
              </select>
              {errors.timeDispatch && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="timeZone">
              Time Zone (Local)
              <br />
              <select
                name="timeZone"
                id="timeZone"
                ref={register({ required: true })}
                className={errors.timeZone && 'error'}
              >
                {timeZoneOptions.map((zone, index) => (
                  <option key={`timeZone-${index}`} value={zone}>
                    {zone}
                  </option>
                ))}
              </select>
              {errors.timeZone && (
                <p className="error">This field is required</p>
              )}
            </label>
          </div>
          <div className="brick">
            {showFieldByVendor(vendorsOptions[1].value) && (
              <>
                <label htmlFor="slaLevel">
                  SLA Level
                  <br />
                  <select
                    name="slaLevel"
                    id="slaLevel"
                    ref={register({ required: true })}
                    className={errors.slaLevel && 'error'}
                  >
                    {slaOptions.map(slaOption => (
                      <option value={slaOption} key={`slaOption-${slaOption}`}>
                        {slaOption}
                      </option>
                    ))}
                  </select>
                  {errors.slaLevel && (
                    <p className="error">This field is required</p>
                  )}
                </label>
                <br />
              </>
            )}
            <label htmlFor="mettelId">
              Bruin Ticket ID <br />
              <input
                type="text"
                name="mettelId"
                id="mettelId"
                ref={register({ required: true })}
                className={errors.mettelId && 'error'}
              />
              {errors.mettelId && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <div htmlFor="vendor">
              Vendor
              <br />
              {vendorsOptions.map(vendorsOption => (
                <label
                  className="checkbox"
                  htmlFor="vendor"
                  key={`vendorsOption-${vendorsOption.value}`}
                >
                  {vendorsOption.name}
                  <input
                    type="checkbox"
                    name="vendor"
                    value={vendorsOption.value}
                    id={vendorsOption.value}
                    ref={register({ required: true })}
                    className={errors.vendor && 'error'}
                    onChange={changeVendor}
                  />
                  <span className="checkmark" />
                </label>
              ))}
              {errors.vendor && <p className="error">This field is required</p>}
            </div>
          </div>
          <p className="section-title">Location</p>
          <div className="brick">
            <label htmlFor="owner">
              Name / Owner
              <br />
              <input
                type="text"
                name="owner"
                id="owner"
                ref={register({ required: true })}
                className={errors.owner && 'error'}
              />
              {errors.owner && <p className="error">This field is required</p>}
            </label>
            <br />
            <label htmlFor="address1">
              Address Line 1<br />
              <input
                type="text"
                name="address1"
                id="address1"
                ref={register({ required: true })}
                className={errors.address1 && 'error'}
              />
              {errors.address1 && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="address2">
              Address Line 2<br />
              <input
                type="text"
                name="address2"
                id="address2"
                ref={register({ required: true })}
                className={errors.address2 && 'error'}
              />
              {errors.address2 && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="city">
              City
              <br />
              <input
                type="text"
                name="city"
                id="city"
                ref={register({ required: true })}
                className={errors.city && 'error'}
              />
              {errors.city && <p className="error">This field is required</p>}
            </label>
            <br />
            <label className="half" htmlFor="state">
              State
              <br />
              <select
                name="state"
                id="state"
                ref={register({ required: true })}
                className={errors.state && 'error'}
              >
                {states.map(state => (
                  <option value={state.name} key={state.abbreviation}>
                    {state.name}
                  </option>
                ))}
              </select>
              {errors.state && <p className="error">This field is required</p>}
            </label>
            <label className="half right" htmlFor="zip">
              Zip Code
              <br />
              <input
                type="text"
                name="zip"
                id="zip"
                ref={register({ required: true })}
                className={errors.zip && 'error'}
              />
              {errors.zip && <p className="error">This field is required</p>}
            </label>
          </div>
          <div className="brick">
            <p className="brick-title">On-Site Contact</p>
            <label className="half" htmlFor="firstName">
              First Name
              <br />
              <input
                type="text"
                name="firstName"
                id="firstName"
                ref={register({ required: true })}
                className={errors.firstName && 'error'}
              />
              {errors.firstName && (
                <p className="error">This field is required</p>
              )}
            </label>
            <label className="half right" htmlFor="lastName">
              Last Name
              <br />
              <input
                type="text"
                name="lastName"
                id="lastName"
                ref={register({ required: true, maxLength: 6 })}
                className={errors.lastName && 'error'}
              />
              {errors.lastName && (
                <p className="error">
                  {errors.lastName?.type === 'required' &&
                    'This field is required'}
                  {errors.lastName?.type === 'maxLength' &&
                    'This input exceed maxLength'}
                </p>
              )}
            </label>
            <br />
            <label htmlFor="phoneNumber">
              Phone Number
              <br />
              <input
                type="number"
                name="phoneNumber"
                id="phoneNumber"
                ref={register({ required: true })}
                className={errors.phoneNumber && 'error'}
              />
              {errors.phoneNumber && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="email">
              Email
              <br />
              <input
                type="email"
                name="email"
                id="email"
                ref={register({ required: true })}
                className={errors.email && 'error'}
              />
              {errors.email && <p className="error">This field is required</p>}
            </label>
          </div>
          <p className="section-title">Details</p>
          <div className="brick">
            {showFieldByVendor(vendorsOptions[1].value) && (
              <>
                <p>Service Type</p>
                {errors.serviceType && (
                  <p className="error">This field is required</p>
                )}

                {serviceTypesOptions.map(serviceTypesOption => (
                  <label
                    className="radio"
                    htmlFor="vendor"
                    key={`serviceTypes-${serviceTypesOption.value}`}
                  >
                    {serviceTypesOption.name}
                    <input
                      type="radio"
                      name="vendor"
                      value={serviceTypesOption.value}
                      id={serviceTypesOption.value}
                      ref={register({ required: true })}
                      className={errors.serviceType ? 'radio error' : 'radio'}
                    />
                    <span className="checkmark" />
                  </label>
                ))}
              </>
            )}

            <label htmlFor="issues">
              Issue(s) Experienced
              <br />
              <textarea
                rows="4"
                cols="50"
                name="issues"
                id="issues"
                ref={register({ required: true })}
                className={errors.issues && 'error'}
              />
              {errors.issues && <p className="error">This field is required</p>}
            </label>
          </div>
          <div className="brick">
            <label htmlFor="materials">
              Materials Needed
              <br />
              <textarea
                rows="4"
                cols="50"
                name="materials"
                id="materials"
                ref={register({ required: true })}
                className={errors.materials && 'error'}
              />
              {errors.materials && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="instructions">
              Arrival Instructions
              <br />
              <textarea
                rows="4"
                cols="50"
                name="instructions"
                id="instructions"
                ref={register({ required: true })}
                className={errors.instructions && 'error'}
              />
              {errors.instructions && (
                <p className="error">This field is required</p>
              )}
            </label>
          </div>
          {/*
          <p className="section-title">Attachments</p>
          <div className="brick">
            <div className="file">
              <label htmlFor="files" className="btn">
                Add File/s
                <input
                  id="files"
                  style={{ visibility: 'hidden' }}
                  type="file"
                  multiple
                  onChange={onChangeHandlerFiles}
                />
              </label>
              {files.length ? (
                <div>
                  <ol>
                    {files.map((file, index) => (
                      <li key={`file-name-${index}`}>
                        {file.name}{' '}
                        <button type="button" onClick={() => deleteFile(index)}>
                          Delete file
                        </button>
                      </li>
                    ))}
                  </ol>
                </div>
              ) : (
                <p>No Files Chosen</p>
              )}
            </div>
          </div>
          */}
          <p className="section-title">Requester</p>
          <div className="brick">
            <label className="half" htmlFor="firstNameRequester">
              First Name
              <br />
              <input
                type="text"
                name="firstNameRequester"
                id="firstNameRequester"
                ref={register({ required: true })}
                className={errors.firstNameRequester && 'error'}
              />
              {errors.firstNameRequester && (
                <p className="error">This field is required</p>
              )}
            </label>
            <label className="half right" htmlFor="lastNameRequester">
              Last Name
              <br />
              <input
                type="text"
                name="lastNameRequester"
                id="lastNameRequester"
                ref={register({ required: true, maxLength: 6 })}
                className={errors.lastNameRequester && 'error'}
              />
              {errors.lastNameRequester && (
                <p className="error">
                  {errors.lastNameRequester?.type === 'required' &&
                    'This field is required'}
                  {errors.lastNameRequester?.type === 'maxLength' &&
                    'This input exceed maxLength'}
                </p>
              )}
            </label>
            <br />
            <label htmlFor="department">
              MelTel Department
              <br />
              <select
                name="department"
                id="department"
                ref={register({ required: true })}
                className={errors.department && 'error'}
              >
                {departmentOptions.map((deparmentOption, index) => (
                  <option key={`department-${index}`} value={deparmentOption}>
                    {deparmentOption}
                  </option>
                ))}
              </select>
              {errors.department && (
                <p className="error">This field is required</p>
              )}
            </label>
          </div>
          <div className="brick">
            <label htmlFor="phoneNumberRequester">
              Pnone Number
              <br />
              <input
                type="number"
                name="phoneNumberRequester"
                id="phoneNumberRequester"
                ref={register({ required: true })}
                className={errors.phoneNumberRequester && 'error'}
              />
              {errors.phoneNumberRequester && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="emailRequester">
              Email
              <br />
              <input
                type="email"
                name="emailRequester"
                id="emailRequester"
                ref={register({ required: true })}
                className={errors.emailRequester && 'error'}
              />
              {errors.emailRequester && (
                <p className="error">This field is required</p>
              )}
            </label>
          </div>
          {isLoading ? (
            <Loading />
          ) : (
            <button className="login" type="submit">
              Submit
            </button>
          )}
          {response && response.error && (
            <p className="error">Error, please try again later</p>
          )}
        </form>
      </div>
    </>
  );
}

NewDispatch.propTypes = {
  authToken: PropTypes.string
};

export default privateRoute(NewDispatch);
