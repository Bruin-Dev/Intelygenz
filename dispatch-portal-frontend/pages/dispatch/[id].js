import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { useRouter } from 'next/router';
import { DispatchService } from '../../services/dispatch/dispatch.service';
import { privateRoute } from '../../components/privateRoute/PrivateRoute';
import Menu from '../../components/menu/Menu';
import Loading from '../../components/loading/Loading';
import {
  StatusButton,
  TYPES_STATUS
} from '../../ui/components/status/StatusButton';
import Modal from '../../components/modal/Modal';
import { config } from '../../config/config';

import './id.scss';
import { Routes } from '../../config/routes';

function DispatchDetail({ authToken }) {
  const router = useRouter();
  const { id } = router.query;
  const { vendor } = router.query;

  const [data, setData] = useState();
  const [isLoading, setIsLoading] = useState(true);

  const [cancelError, setCancelError] = useState(false);
  const cancelDispatch = async res => {
    setIsLoading(true);
    setCancelError(false);
    const response = await new DispatchService().update(id, vendor);

    if (response && !response.error) {
      router.push(`${Routes.BASE()}?redirect=?true`);
    } else {
      setCancelError(true);
    }

    setIsLoading(false);
  };

  useEffect(() => {
    let response;
    async function getInfoDispatch() {
      response = await new DispatchService().get(id, vendor);

      if (response && !response.error) {
        setData(response);
      }
      setIsLoading(false);
    }
    getInfoDispatch();
  }, [id, vendor]);

  if (isLoading) {
    return (
      <div data-testid="dispatch-detail-loading-page">
        <Menu authToken={authToken} />
        {isLoading && <Loading />}
      </div>
    );
  }

  return (
    <div data-testid="dispatch-detail-page">
      <Menu authToken={authToken} />
      {!data ? (
        <button
          type="button"
          className="float-center text-red-500 border border-red-500 text-base px-1 m-8 rounded inline-flex items-center cursor-not-allowed"
        >
          There are problems obtaining the requested information.
        </button>
      ) : (
        <div>
          {data && data.status && data.status !== TYPES_STATUS.cancelled.value && (
            <div className="flex flex-col pt-2 px-10">
              <div className="block">
                <div className="float-right flex flex-col">
                  <Modal
                    callbackResult={cancelDispatch}
                    buttonText="Cancel dispatch"
                    titleModal="Cancel dispatch"
                    textModal="Are you sure to cancel this dispatch?"
                  />
                </div>
              </div>
              <div className="block">
                <div className="float-right flex flex-col">
                  {cancelError && (
                    <p className="text-red-500 text-sm px-1">
                      There is a problem processing the request. Try it again
                      later.
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          <div className="flex flex-wrap m-8 border-solid border-2 border-gray-400">
            <div className="w-full md:w-1/4 flex-none p-4 bg-gray-300 justify-between">
              <div className="mb-8">
                <div className="text-gray-900 font-bold text-xl mb-2">
                  Vendor Details
                </div>

                <p className="text-gray-700 text-sm">
                  <b>Vendor:</b>{' '}
                  <span data-test-id="dispatch-detail-vendor">
                    {data.vendor}
                  </span>
                </p>
                <p className="text-gray-700 text-sm">
                  <b>SLA Level:</b>{' '}
                  <span data-test-id="dispatch-detail-slaLevel">
                    {data.slaLevel}
                  </span>
                </p>
                <p className="text-gray-700 text-sm">
                  <b>Mettel Id:</b>{' '}
                  <span data-test-id="dispatch-detail-id">{data.id}</span>
                </p>
                <p className="text-gray-700 text-sm">
                  <b>Bruin Ticket Id:</b>{' '}
                  <span data-test-id="dispatch-detail-bruin-id">
                    {data.mettelId}
                  </span>
                </p>
                <p className="text-gray-700 text-sm">
                  <b>Date of dispatch:</b>{' '}
                  <span data-test-id="dispatch-detail-dateDispatch">
                    {data.dateDispatch}
                  </span>
                </p>
                <p className="text-gray-700 text-sm">
                  <b>Local time of dispatch:</b>{' '}
                  <span data-test-id="dispatch-detail-timeDispatch">
                    {data.timeDispatch}
                  </span>
                </p>
                <p className="text-gray-700 text-sm">
                  <b>Time Zone Local:</b>{' '}
                  <span data-test-id="dispatch-detail-timeZone">
                    {data.timeZone}
                  </span>
                </p>
                <p className="text-gray-700 text-sm">
                  <b>Status:</b>{' '}
                  <span data-test-id="dispatch-detail-status">
                    <StatusButton status={data.status} />
                  </span>
                </p>
              </div>
            </div>
            <div className="w-full md:w-1/4 bg-white p-4 flex flex-col justify-between leading-normal">
              <div className="mb-8">
                <div className="mb-4">
                  <div className="text-gray-900 font-bold text-xl mb-2">
                    Requester
                  </div>
                  <p className="text-gray-900 text-sm">
                    Name:{' '}
                    <span data-test-id="dispatch-detail-requester-name">
                      {data.requester.name}
                    </span>
                  </p>
                  <p className="text-gray-900 text-sm">
                    Email:{' '}
                    <span data-test-id="dispatch-detail-requester-email">
                      {data.requester.email}
                    </span>
                  </p>
                  <p className="text-gray-900 text-sm">
                    Department:{' '}
                    <span data-test-id="dispatch-detail-requester-department">
                      {data.requester.department}
                    </span>
                  </p>
                  <p className="text-gray-900 text-sm">
                    Phone number:{' '}
                    <span data-test-id="dispatch-detail-requester-phoneNumber">
                      {data.requester.phoneNumber}
                    </span>
                  </p>
                </div>

                <div className="mb-4">
                  <div className="text-gray-900 font-bold text-xl mb-2">
                    On-Site Contact
                  </div>
                  <p className="text-gray-900 text-sm">
                    Site:{' '}
                    <span data-test-id="dispatch-detail-onSiteContact-site">
                      {data.onSiteContact.site}
                    </span>
                  </p>
                  <p className="text-gray-900 text-sm">
                    Street:{' '}
                    <span data-test-id="dispatch-detail-onSiteContact-street">
                      {data.onSiteContact.street}
                    </span>
                  </p>
                  <p className="text-gray-900 text-sm">
                    City:{' '}
                    <span data-test-id="dispatch-detail-onSiteContact-city">
                      {data.onSiteContact.city}
                    </span>
                  </p>
                  <p className="text-gray-900 text-sm">
                    State:{' '}
                    <span data-test-id="dispatch-detail-onSiteContact-state">
                      {data.onSiteContact.state}
                    </span>
                  </p>
                  <p className="text-gray-900 text-sm">
                    Zip:{' '}
                    <span data-test-id="dispatch-detail-onSiteContact-zip">
                      {data.onSiteContact.zip}
                    </span>
                  </p>
                  <p className="text-gray-900 text-sm">
                    Phone number:{' '}
                    <span data-test-id="dispatch-detail-onSiteContact-phoneNumber">
                      {data.onSiteContact.phoneNumber}
                    </span>
                  </p>
                  <p className="text-gray-900 text-sm">
                    Name:{' '}
                    <span data-test-id="dispatch-detail-onSiteContact-phoneNumber">
                      {data.onSiteContact.name}
                    </span>
                  </p>
                </div>

                <div className="mb-4">
                  <div className="text-gray-900 font-bold text-xl mb-2">
                    Field Engineer
                  </div>
                  <p className="text-gray-900 text-sm">
                    Name:{' '}
                    <span data-test-id="dispatch-detail-fieldEngineer-name">
                      {data.fieldEngineer.name}
                    </span>
                  </p>
                  <p className="text-gray-900 text-sm">
                    Phone:{' '}
                    <span data-test-id="dispatch-detail-fieldEngineer-phone">
                      {data.fieldEngineer.phoneNumber}
                    </span>
                  </p>
                </div>
              </div>
            </div>

            <div className="w-full md:w-2/4 bg-white p-4 flex flex-col justify-between leading-normal">
              <div className="mb-8">
                <div className="text-gray-900 font-bold text-xl mb-2">
                  Details
                </div>

                <p className="text-gray-900 text-sm">
                  Service type:{' '}
                  <span data-test-id="dispatch-detail-details-serviceType">
                    {data.details.serviceType}
                  </span>
                </p>
                <p className="text-gray-900 text-sm">
                  Instructions:{' '}
                  <span data-test-id="dispatch-detail-details-instructions">
                    {data.details.instructions}
                  </span>
                </p>
                <p className="text-gray-900 text-sm">
                  Information:{' '}
                  <span data-test-id="dispatch-detail-details-information">
                    {data.details.information}
                  </span>
                </p>
                <p className="text-gray-900 text-sm">
                  Materials:{' '}
                  <span data-test-id="dispatch-detail-details-materials">
                    {data.details.materials}
                  </span>
                </p>

                {data.vendor === config.VENDORS.CTS && (
                  <p className="text-gray-900 text-sm">
                    Rest of parameters:{' '}
                    <span
                      data-test-id="dispatch-detail-details-fieldEngineer"
                      style={{ whiteSpace: 'break-spaces' }}
                    >
                      {data.details.res}
                    </span>
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

DispatchDetail.propTypes = {
  authToken: PropTypes.string
};

export default privateRoute(DispatchDetail);
