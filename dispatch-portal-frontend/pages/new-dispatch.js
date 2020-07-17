import PropTypes from 'prop-types';
import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useForm } from 'react-hook-form';
import { privateRoute } from '../components/privateRoute/PrivateRoute';
import Menu from '../components/menu/Menu';
import Loading from '../components/loading/Loading';
import { DispatchService } from '../services/dispatch/dispatch.service';
import { Routes } from '../config/routes';
import {
  statesCanada,
  statesPR,
  statesUSA
} from '../config/constants/states.constants';
import {
  countryOptions,
  timeOptions,
  vendorsOptions,
  timeZoneOptions,
  departmentOptions,
  serviceTypesOptions,
  slaLevelOptions,
  requesterPhoneNumberOptions
} from '../config/constants/dispatch.constants';
import { config } from '../config/config';
import './new-dispatch.scss';
import VendorDispatchLink from '../ui/components/vendorDispatchLink/VendorDispatchLink';

function NewDispatch({ authToken }) {
  const router = useRouter();
  const { register, handleSubmit, errors } = useForm();
  const [response, setResponse] = useState({
    data: [],
    errors: []
  });
  const [isLoading, setIsLoading] = useState(false);
  const [blockedVendors, setBlockedVendors] = useState([]);
  const [statesOptions, setStatesOptions] = useState(statesUSA);
  const [selectedVendor, setSelectedVendor] = useState([]); // Note: ['CTS'] ['LIT'] ['CTS', 'LIT']
  const dispatchService = new DispatchService();

  const onSubmit = async formData => {
    setIsLoading(true);

    const resAux = {};
    resAux.data = [];
    resAux.errors = [];

    /** **
     *
     * Explanation:
     * - Send as many calls as vendors are selected.
     * - Cases:
     * 1) Everything OK: redirect to Dashboard.
     * 2) All KO: show error.
     * 3) Some fail and others do not: block the vendors that have been OK and show error in the other vendors.
     *
     */
    await Promise.all(
      formData.vendor.map(async vendor => {
        const resData = await dispatchService.newDispatch(formData, vendor);

        if (resData && resData.error) {
          resAux.errors.push({
            message: resData.error,
            vendor
          });
          return;
        }

        if (resData && resData.data && resData.data.id) {
          resAux.data.push({
            data: resData,
            vendor
          });
          setBlockedVendors([...blockedVendors, vendor]);
        }
      })
    );

    // Check error
    if (resAux.errors.length) {
      setResponse(resAux);
      setIsLoading(false);
      return;
    }

    // Success
    router.push(`${Routes.BASE()}`);
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

  const changeCountry = country => {
    if (country === countryOptions[1]) {
      setStatesOptions(statesCanada);
      return;
    }

    if (country === countryOptions[2]) {
      setStatesOptions(statesPR);
      return;
    }

    if (country === countryOptions[0]) {
      setStatesOptions(statesUSA);
    }
  };

  const showFieldByVendor = vendor => selectedVendor.includes(vendor);

  return (
    <div data-testid="newDispatch-page-component">
      <Menu authToken={authToken} />
      <div className="new-dispatch-wrapper">
        <p className="form-title">New Dispatch Request</p>

        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="flex">
            <div className="w-full md:w-1/2 p-8">
              <div className="flex flex-col">
                <div className="-mx-3 md:flex mb-6">
                  <div className="md:w-1/2 px-3 mb-6 md:mb-0">
                    <label
                      className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                      htmlFor="dateDispatch"
                    >
                      Date of dispatch
                      <input
                        className={
                          errors.dateDispatch
                            ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                            : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                        }
                        type="date"
                        name="dateDispatch"
                        data-testid="dateDispatch"
                        id="dateDispatch"
                        ref={register({ required: true })}
                      />
                      {errors.dateDispatch && (
                        <p className="text-red-500 text-xs italic">
                          This field is required
                        </p>
                      )}
                    </label>
                  </div>
                  <div className="md:w-1/2 px-3">
                    <label
                      className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                      htmlFor="timeDispatch"
                    >
                      Time of dispatch (Local)
                      <div className="relative">
                        <select
                          name="timeDispatch"
                          data-testid="timeDispatch"
                          id="timeDispatch"
                          ref={register({ required: true })}
                          className={
                            errors.timeDispatch
                              ? 'block appearance-none w-full bg-grey-lighter border border-red-300 text-grey-darker py-3 px-4 pr-8 rounded'
                              : 'block appearance-none w-full bg-grey-lighter border border-grey-lighter text-grey-darker py-3 px-4 pr-8 rounded'
                          }
                        >
                          {timeOptions.map(time => (
                            <option value={time} key={`time-${time}`}>
                              {time}
                            </option>
                          ))}
                        </select>
                        <div
                          className="pointer-events-none absolute pin-y pin-r flex items-center px-2 text-grey-darker"
                          style={{ top: '13px', right: '0px' }}
                        >
                          <svg
                            className="h-4 w-4"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                          >
                            <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                          </svg>
                        </div>
                      </div>
                      {errors.timeDispatch && (
                        <p className="text-red-500 text-xs italic">
                          This field is required
                        </p>
                      )}
                    </label>
                  </div>
                </div>
              </div>

              <div className="flex flex-col">
                <div className="md:w-1/2 pr-3 mb-6 md:mb-0">
                  <label
                    className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                    htmlFor="timeZone"
                  >
                    Time Zone (Local)
                    <div className="relative">
                      <select
                        name="timeZone"
                        data-testid="timeZone"
                        id="timeZone"
                        ref={register({ required: true })}
                        className={
                          errors.timeZone
                            ? 'block appearance-none w-full bg-grey-lighter border border-red-300 text-grey-darker py-3 px-4 pr-8 rounded'
                            : 'block appearance-none w-full bg-grey-lighter border border-grey-lighter text-grey-darker py-3 px-4 pr-8 rounded'
                        }
                      >
                        {timeZoneOptions.map((zone, index) => (
                          <option key={`timeZone-${index}`} value={zone.name}>
                            {zone.name}
                          </option>
                        ))}
                      </select>
                      <div
                        className="pointer-events-none absolute pin-y pin-r flex items-center px-2 text-grey-darker"
                        style={{ top: '13px', right: '0px' }}
                      >
                        <svg
                          className="h-4 w-4"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                        </svg>
                      </div>
                    </div>
                    {errors.timeZone && (
                      <p className="text-red-500 text-xs italic">
                        This field is required
                      </p>
                    )}
                  </label>
                </div>
              </div>
            </div>

            <div className="w-full md:w-1/2 p-8">
              <div className="flex flex-col">
                <div className="block uppercase tracking-wide text-grey-darker text-sm mb-2">
                  Vendor
                </div>
                {vendorsOptions.map(vendorsOption =>
                  blockedVendors.find(r => vendorsOption.value === r) ? (
                    ''
                  ) : (
                    <label
                      className="flex justify-start items-start"
                      htmlFor="vendor"
                      key={`vendorsOption-${vendorsOption.value}`}
                    >
                      <div
                        className={
                          errors.vendor
                            ? 'bg-white border-2 rounded border-red-500 w-6 h-6 flex flex-shrink-0 justify-center items-center mr-2 mb-4 focus-within:border-blue-500'
                            : 'bg-white border-2 rounded border-gray-400 w-6 h-6 flex flex-shrink-0 justify-center items-center mr-2 mb-4 focus-within:border-blue-500'
                        }
                      >
                        <input
                          type="checkbox"
                          name="vendor"
                          value={vendorsOption.value}
                          id={vendorsOption.value}
                          data-testid={`${vendorsOption.value}-checkbox`}
                          ref={register({ required: true })}
                          className="opacity-0 absolute rounded"
                          onChange={changeVendor}
                        />
                        <svg
                          className="fill-current hidden w-4 h-4 text-green-500 pointer-events-none"
                          viewBox="0 0 20 20"
                        >
                          <path d="M0 11l2-2 5 5L18 3l2 2L7 18z" />
                        </svg>
                      </div>
                      <div className="select-none">{vendorsOption.name}</div>
                    </label>
                  )
                )}
                {errors.vendor && (
                  <p className="text-red-500 text-xs italic">
                    This field is required
                  </p>
                )}
              </div>

              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="mettelId"
                >
                  Bruin Ticket ID
                  <input
                    className={
                      errors.mettelId
                        ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                    type="text"
                    name="mettelId"
                    data-testid="mettelId"
                    id="mettelId"
                    ref={register({ required: true })}
                    placeholder="458788998"
                  />
                  {errors.mettelId && (
                    <p className="text-red-500 text-xs italic">
                      This field is required
                    </p>
                  )}
                </label>
              </div>

              {showFieldByVendor(config.VENDORS.CTS) && (
                <div className="flex flex-col" data-testid="cts-field">
                  <label
                    className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                    htmlFor="slaLevel"
                  >
                    Sla Level (only for {config.VENDORS.CTS})
                    <div className="relative">
                      <select
                        name="slaLevel"
                        data-testid="slaLevel"
                        id="slaLevel"
                        ref={register({ required: true })}
                        className={
                          errors.slaLevel
                            ? 'block appearance-none w-full bg-grey-lighter border border-red-300 text-grey-darker py-3 px-4 pr-8 rounded'
                            : 'block appearance-none w-full bg-grey-lighter border border-grey-lighter text-grey-darker py-3 px-4 pr-8 rounded'
                        }
                      >
                        {slaLevelOptions.map((slaLeveloption, index) => (
                          <option
                            key={`slaLeveloption-${index}`}
                            value={slaLeveloption}
                          >
                            {slaLeveloption}
                          </option>
                        ))}
                      </select>
                      <div
                        className="pointer-events-none absolute pin-y pin-r flex items-center px-2 text-grey-darker"
                        style={{ top: '13px', right: '0px' }}
                      >
                        <svg
                          className="h-4 w-4"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                        </svg>
                      </div>
                    </div>
                    {errors.country && (
                      <p className="text-red-500 text-xs italic">
                        This field is required
                      </p>
                    )}
                  </label>
                </div>
              )}
            </div>
          </div>

          <div className="flex">
            <div className="w-1/2 px-8">
              <div className="w-full mb-4">
                <p className="text-grey-darker text-2xl">Location</p>
              </div>
              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="owner"
                >
                  Name / Owner
                  <input
                    className={
                      errors.owner
                        ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                    type="text"
                    name="owner"
                    data-testid="owner"
                    id="owner"
                    ref={register({ required: true })}
                    placeholder="James"
                  />
                  {errors.owner && (
                    <p className="text-red-500 text-xs italic">
                      This field is required
                    </p>
                  )}
                </label>
              </div>

              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="address1"
                >
                  Address Line 1
                  <input
                    className={
                      errors.address1
                        ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                    type="text"
                    name="address1"
                    data-testid="address1"
                    id="address1"
                    ref={register({ required: true })}
                    placeholder="88 St Laurent Dr"
                  />
                  {errors.address1 && (
                    <p className="text-red-500 text-xs italic">
                      This field is required
                    </p>
                  )}
                </label>
              </div>
              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="address2"
                >
                  Address Line 2
                  <input
                    className="appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1"
                    type="text"
                    name="address2"
                    data-testid="address2"
                    id="address2"
                    placeholder="Clark"
                    ref={register({})}
                  />
                </label>
              </div>

              {showFieldByVendor(config.VENDORS.CTS) && (
                <div className="flex flex-col">
                  <label
                    className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                    htmlFor="department"
                  >
                    Country (only for {config.VENDORS.CTS})
                    <div className="relative">
                      <select
                        name="country"
                        data-testid="country"
                        id="country"
                        ref={register({ required: true })}
                        className={
                          errors.country
                            ? 'block appearance-none w-full bg-grey-lighter border border-red-300 text-grey-darker py-3 px-4 pr-8 rounded'
                            : 'block appearance-none w-full bg-grey-lighter border border-grey-lighter text-grey-darker py-3 px-4 pr-8 rounded'
                        }
                        onChange={e => changeCountry(e.target.value)}
                      >
                        {countryOptions.map((countryOption, index) => (
                          <option
                            key={`country-${index}`}
                            value={countryOption}
                          >
                            {countryOption}
                          </option>
                        ))}
                      </select>
                      <div
                        className="pointer-events-none absolute pin-y pin-r flex items-center px-2 text-grey-darker"
                        style={{ top: '13px', right: '0px' }}
                      >
                        <svg
                          className="h-4 w-4"
                          xmlns="http://www.w3.org/2000/svg"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                        </svg>
                      </div>
                    </div>
                    {errors.country && (
                      <p className="text-red-500 text-xs italic">
                        This field is required
                      </p>
                    )}
                  </label>
                </div>
              )}

              <div className="flex flex-col">
                <div className="-mx-3 md:flex mb-2">
                  <div className="md:w-1/2 px-3 mb-6 md:mb-0">
                    <label
                      className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                      htmlFor="city"
                    >
                      City
                      <input
                        className={
                          errors.city
                            ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                            : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                        }
                        type="text"
                        name="city"
                        data-testid="city"
                        id="city"
                        ref={register({ required: true })}
                        placeholder="Nueva jersey"
                      />
                      {errors.city && (
                        <p className="text-red-500 text-xs italic">
                          This field is required
                        </p>
                      )}
                    </label>
                  </div>
                  <div className="md:w-1/2 px-3">
                    <label
                      className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                      htmlFor="state"
                    >
                      State
                      <div className="relative">
                        <select
                          name="state"
                          data-testid="state"
                          id="state"
                          ref={register({ required: true })}
                          className={
                            errors.state
                              ? 'block appearance-none w-full bg-grey-lighter border border-red-300 text-grey-darker py-3 px-4 pr-8 rounded'
                              : 'block appearance-none w-full bg-grey-lighter border border-grey-lighter text-grey-darker py-3 px-4 pr-8 rounded'
                          }
                        >
                          {statesOptions.map(state => (
                            <option value={state.name} key={state.abbreviation}>
                              {state.name}
                            </option>
                          ))}
                        </select>
                        <div
                          className="pointer-events-none absolute pin-y pin-r flex items-center px-2 text-grey-darker"
                          style={{ top: '13px', right: '0px' }}
                        >
                          <svg
                            className="h-4 w-4"
                            xmlns="http://www.w3.org/2000/svg"
                            viewBox="0 0 20 20"
                          >
                            <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                          </svg>
                        </div>
                      </div>
                      {errors.state && (
                        <p className="text-red-500 text-xs italic">
                          This field is required
                        </p>
                      )}
                    </label>
                  </div>
                  <div className="md:w-1/2 px-3">
                    <label
                      className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                      htmlFor="zip"
                    >
                      Zip Code
                      <input
                        className={
                          errors.zip
                            ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                            : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                        }
                        type="text"
                        name="zip"
                        data-testid="zip"
                        id="zip"
                        ref={register({ required: true })}
                        placeholder="07097"
                      />
                      {errors.zip && (
                        <p className="text-red-500 text-xs italic">
                          This field is required
                        </p>
                      )}
                    </label>
                  </div>
                </div>
              </div>
            </div>

            <div className="w-1/2 px-8">
              <div className="w-full mb-4">
                <p className="text-grey-darker text-2xl">On-Site Contact</p>
              </div>

              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="firstName"
                >
                  First Name
                  <input
                    className={
                      errors.firstName
                        ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                    type="text"
                    name="firstName"
                    data-testid="firstName"
                    id="firstName"
                    ref={register({ required: true })}
                    placeholder="Helen"
                  />
                  {errors.firstName && (
                    <p className="text-red-500 text-xs italic">
                      This field is required
                    </p>
                  )}
                </label>
              </div>

              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="lastName"
                >
                  Last Name
                  <input
                    className={
                      errors.lastName
                        ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                    type="text"
                    name="lastName"
                    data-testid="lastName"
                    id="lastName"
                    ref={register({ required: true })}
                    placeholder="MacLow"
                  />
                  {errors.lastName && (
                    <p className="text-red-500 text-xs italic">
                      {errors.lastName?.type === 'required' &&
                        'This field is required'}
                      {errors.lastName?.type === 'maxLength' &&
                        'This input exceeds the maximum length of 10 characters'}
                    </p>
                  )}
                </label>
              </div>

              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="phoneNumber"
                >
                  Phone Number
                  <input
                    className={
                      errors.phoneNumber
                        ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                    type="text"
                    name="phoneNumber"
                    data-testid="phoneNumber"
                    id="phoneNumber"
                    ref={register({ required: true })}
                    placeholder="+1 587897524"
                  />
                  {errors.phoneNumber && (
                    <p className="text-red-500 text-xs italic">
                      This field is required
                    </p>
                  )}
                </label>
              </div>
            </div>
          </div>

          <div className="flex">
            <div className="w-full mb-2 pl-8">
              <p className="text-grey-darker text-2xl">Details</p>
            </div>
          </div>

          <div className="flex">
            <div className="w-1/2 px-8">
              {showFieldByVendor(config.VENDORS.CTS) && (
                <div className="flex flex-col">
                  <div className="block uppercase tracking-wide text-grey-darker text-sm mb-2">
                    Service Type (only for {config.VENDORS.CTS})
                  </div>
                  {serviceTypesOptions.map(serviceTypesOption => (
                    <label
                      className="flex justify-start items-start"
                      htmlFor="serviceType"
                      key={`serviceTypes-${serviceTypesOption.value}`}
                    >
                      <div
                        className={
                          errors.vendor
                            ? 'bg-white border-2 rounded border-red-500 w-6 h-6 flex flex-shrink-0 justify-center items-center mr-2 mb-4 focus-within:border-blue-500'
                            : 'bg-white border-2 rounded border-gray-400 w-6 h-6 flex flex-shrink-0 justify-center items-center mr-2 mb-4 focus-within:border-blue-500'
                        }
                      >
                        <input
                          type="checkbox"
                          name="serviceType"
                          data-testid="serviceType"
                          value={serviceTypesOption.value}
                          id={serviceTypesOption.value}
                          ref={register({ required: true })}
                          className="opacity-0 absolute rounded"
                        />
                        <svg
                          className="fill-current hidden w-4 h-4 text-green-500 pointer-events-none"
                          viewBox="0 0 20 20"
                        >
                          <path d="M0 11l2-2 5 5L18 3l2 2L7 18z" />
                        </svg>
                      </div>
                      <div className="select-none">
                        {serviceTypesOption.name}
                      </div>
                    </label>
                  ))}
                  {errors.serviceType && (
                    <p className="text-red-500 text-xs italic">
                      This field is required
                    </p>
                  )}
                </div>
              )}
              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="issues"
                >
                  Issue(s) Experienced
                  <textarea
                    rows="4"
                    cols="50"
                    name="issues"
                    data-testid="issues"
                    id="issues"
                    ref={register({ required: true })}
                    placeholder="Write your issues here ...."
                    className={
                      errors.issues
                        ? 'appearance-none w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                  />
                  {errors.issues && (
                    <p className="text-red-500 text-xs italic">
                      This field is required
                    </p>
                  )}
                </label>
              </div>
            </div>

            <div className="w-1/2 px-8">
              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="materials"
                >
                  Materials Needed
                  <textarea
                    rows="4"
                    cols="50"
                    name="materials"
                    data-testid="materials"
                    id="materials"
                    ref={register({ required: true })}
                    placeholder="Write your comments here ...."
                    className={
                      errors.materials
                        ? 'appearance-none w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                  />
                  {errors.materials && (
                    <p className="text-red-500 text-xs italic">
                      This field is required
                    </p>
                  )}
                </label>
              </div>
              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="instructions"
                >
                  Arrival Instructions
                  <textarea
                    rows="4"
                    cols="50"
                    name="instructions"
                    data-testid="instructions"
                    id="instructions"
                    placeholder="Write your instructions here ...."
                    ref={register({ required: true })}
                    className={
                      errors.instructions
                        ? 'appearance-none w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                  />
                  {errors.instructions && (
                    <p className="text-red-500 text-xs italic">
                      This field is required
                    </p>
                  )}
                </label>
              </div>
            </div>
          </div>

          <div className="flex">
            <div className="w-full mb-2 pl-8">
              <p className="text-grey-darker text-2xl">Requester</p>
            </div>
          </div>

          <div className="flex pb-8">
            <div className="w-1/2 px-8">
              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="firstNameRequester"
                >
                  Name
                  <input
                    className={
                      errors.firstNameRequester
                        ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                    type="text"
                    name="firstNameRequester"
                    data-testid="firstNameRequester"
                    id="firstNameRequester"
                    placeholder="Pullman"
                    ref={register({ required: true })}
                  />
                  {errors.firstNameRequester && (
                    <p className="text-red-500 text-xs italic">
                      {errors.firstNameRequester?.type === 'required' &&
                        'This field is required'}
                      {errors.firstNameRequester?.type === 'maxLength' &&
                        'This input exceeds the maximum length of 10 characters'}{' '}
                    </p>
                  )}
                </label>
              </div>
              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="lastNameRequester"
                >
                  Last Name
                  <input
                    className={
                      errors.lastNameRequester
                        ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                    type="text"
                    name="lastNameRequester"
                    data-testid="lastNameRequester"
                    id="lastNameRequester"
                    placeholder="Kidman"
                    ref={register({ required: true })}
                  />
                  {errors.lastNameRequester && (
                    <p className="text-red-500 text-xs italic">
                      {errors.lastNameRequester?.type === 'required' &&
                        'This field is required'}
                      {errors.lastNameRequester?.type === 'maxLength' &&
                        'This input exceeds the maximum length of 10 characters'}{' '}
                    </p>
                  )}
                </label>
              </div>
              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="department"
                >
                  MetTel Department
                  <div className="relative">
                    <select
                      name="department"
                      data-testid="department"
                      id="department"
                      ref={register({ required: true })}
                      className={
                        errors.department
                          ? 'block appearance-none w-full bg-grey-lighter border border-red-300 text-grey-darker py-3 px-4 pr-8 rounded'
                          : 'block appearance-none w-full bg-grey-lighter border border-grey-lighter text-grey-darker py-3 px-4 pr-8 rounded'
                      }
                    >
                      {departmentOptions.map((deparmentOption, index) => (
                        <option
                          key={`department-${index}`}
                          value={deparmentOption}
                        >
                          {deparmentOption}
                        </option>
                      ))}
                    </select>
                    <div
                      className="pointer-events-none absolute pin-y pin-r flex items-center px-2 text-grey-darker"
                      style={{ top: '13px', right: '0px' }}
                    >
                      <svg
                        className="h-4 w-4"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                      </svg>
                    </div>
                  </div>
                  {errors.department && (
                    <p className="text-red-500 text-xs italic">
                      This field is required
                    </p>
                  )}
                </label>
              </div>
            </div>

            <div className="w-1/2 px-8">
              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="phoneNumberRequester"
                >
                  Phone Number
                  <div className="relative">
                    <select
                      name="phoneNumberRequester"
                      data-testid="phoneNumberRequester"
                      id="phoneNumberRequester"
                      ref={register({ required: true })}
                      className={
                        errors.phoneNumberRequester
                          ? 'block appearance-none w-full bg-grey-lighter border border-red-300 text-grey-darker py-3 px-4 pr-8 rounded'
                          : 'block appearance-none w-full bg-grey-lighter border border-grey-lighter text-grey-darker py-3 px-4 pr-8 rounded'
                      }
                    >
                      {requesterPhoneNumberOptions.map(
                        requesterPhoneNumberOption => (
                          <option
                            value={requesterPhoneNumberOption.value}
                            key={`requesterPhoneNumberOption-${requesterPhoneNumberOption.value}`}
                          >
                            {requesterPhoneNumberOption.label}
                          </option>
                        )
                      )}
                    </select>
                    <div
                      className="pointer-events-none absolute pin-y pin-r flex items-center px-2 text-grey-darker"
                      style={{ top: '13px', right: '0px' }}
                    >
                      <svg
                        className="h-4 w-4"
                        xmlns="http://www.w3.org/2000/svg"
                        viewBox="0 0 20 20"
                      >
                        <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                      </svg>
                    </div>
                  </div>
                  {errors.phoneNumberRequester && (
                    <p className="text-red-500 text-xs italic">
                      This field is required
                    </p>
                  )}
                </label>
              </div>
              <div className="flex flex-col">
                <label
                  className="block uppercase tracking-wide text-grey-darker text-sm mb-2"
                  htmlFor="emailRequester"
                >
                  Email
                  <input
                    className={
                      errors.emailRequester
                        ? 'appearance-none block w-full bg-grey-lighter text-red-300 border border-red-500 rounded py-3 px-4 mb-1'
                        : 'appearance-none block w-full bg-grey-lighter text-grey-darker border rounded py-3 px-4 mb-1'
                    }
                    type="text"
                    name="emailRequester"
                    data-testid="emailRequester"
                    id="emailRequester"
                    ref={register({
                      required: true,
                      pattern: {
                        value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}$/i,
                        message: 'Incorrect format: example@example.com'
                      }
                    })}
                    placeholder="example1@example.com"
                  />
                  {errors.emailRequester && (
                    <p className="text-red-500 text-xs italic">
                      {errors.emailRequester?.type === 'required' &&
                        'This field is required'}
                      {errors.emailRequester.message}
                    </p>
                  )}
                </label>
              </div>
            </div>
          </div>

          <div className="flex flex-row-reverse content-center px-8">
            {isLoading ? (
              <Loading data-testid="loading-new-dispatch-page" />
            ) : (
              <button
                className="bg-teal-500 hover:bg-teal-700 text-white center py-2 px-4 rounded"
                type="submit"
                data-test-id="new-dispatch-submit"
              >
                Submit
              </button>
            )}
            {response && response.errors.length ? (
              <p
                className="text-red-500 text-base italic py-2 mx-5"
                data-testid="error-new-dispatch-page"
              >
                {response.errors.length === vendorsOptions.length
                  ? 'Error, please try again later'
                  : `Error in one of the vendors: ${response.errors.map(
                      error => error.vendor
                    )}   `}
              </p>
            ) : (
              ''
            )}

            {response && response.data.length ? (
              <p
                className="text-green-500 text-base italic py-2 mx-5"
                data-testid="error-new-dispatch-page"
              >
                The following dispatches have been created correctly for these
                vendors:{' '}
                {response.data.map(resData => (
                  <VendorDispatchLink
                    dispatchId={resData.data.data.id}
                    vendor={resData.vendor}
                  />
                ))}
              </p>
            ) : (
              ''
            )}
          </div>
        </form>
      </div>
    </div>
  );
}

NewDispatch.propTypes = {
  authToken: PropTypes.string
};

export default privateRoute(NewDispatch);
