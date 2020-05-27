import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { useRouter } from 'next/router';
import { dispatchService } from '../../services/dispatch/dispatch.service';
import { privateRoute } from '../../components/privateRoute/PrivateRoute';
import Menu from '../../components/menu/Menu';
import Loading from '../../components/loading/Loading';
import { config } from '../../config/config';
import './id.scss';

function Dispatch({ authToken }) {
  const router = useRouter();
  const { id } = router.query;

  const [data, setData] = useState();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function getInfoDispatch() {
      const response = await dispatchService.get(id);

      if (response && !response.error) {
        setData(response);
      }
      setIsLoading(false);
    }
    getInfoDispatch();
  }, [id]);

  return (
    <div>
      <Menu authToken={authToken} />
      {isLoading && <Loading />}
      {!data ? (
        <p>Not found dispatch</p>
      ) : (
        <div className="flex m-8">
          <div className="w-1/4 border-b border-l lg:h-auto lg:border-t lg:border-gray-400 flex-none rounded-t lg:rounded-t-none lg:rounded-l bg-gray-300 p-4 justify-between">
            <div className="mb-8">
              <div className="text-gray-900 font-bold text-xl mb-2">
                Vendor Details
              </div>

              <p className="text-gray-700 text-sm">
                <b>Vendor:</b> {data.vendor}
              </p>
              <p className="text-gray-700 text-sm">
                <b>SLA Level:</b> {data.slaLevel}
              </p>
              <p className="text-gray-700 text-sm">
                <b>Bruin Ticket ID:</b> {data.mettelId}
              </p>
              <p className="text-gray-700 text-sm">
                <b>Local time of dispatch:</b> {data.timeDispatch}
              </p>
              <p className="text-gray-700 text-sm">
                <b>Time Zone Local:</b> {data.timeZone}
              </p>
              <p className="text-gray-700 text-sm">
                <b>Status:</b>{' '}
                <button type="button" className={data.status}>
                  {' '}
                  {/* Todo: repair status button */}
                  {data.status}
                </button>
              </p>
            </div>
          </div>
          <div className="w-2/4 border-r border-b border-l border-gray-400 lg:border-l-0 lg:border-r-0 lg:border-t lg:border-gray-400 bg-white p-4 flex flex-col justify-between leading-normal">
            <div className="mb-8">
              <div className="mb-4">
                <div className="text-gray-900 font-bold text-xl mb-2">
                  Requester
                </div>
                <p className="text-gray-900 text-sm">
                  Name: {data.requester.name}
                </p>
                <p className="text-gray-900 text-sm">
                  Email: {data.requester.email}
                </p>
                <p className="text-gray-900 text-sm">
                  Department: {data.requester.department}
                </p>
                <p className="text-gray-900 text-sm">
                  Phone number: {data.requester.phoneNumber}
                </p>
              </div>

              <div className="text-gray-900 font-bold text-xl mb-2">
                On-Site Contact
              </div>
              <p className="text-gray-900 text-sm">
                Site: {data.onSiteContact.site}
              </p>
              <p className="text-gray-900 text-sm">
                Street: {data.onSiteContact.street}
              </p>
              <p className="text-gray-900 text-sm">
                City: {data.onSiteContact.city}
              </p>
              <p className="text-gray-900 text-sm">
                State: {data.onSiteContact.state}
              </p>
              <p className="text-gray-900 text-sm">
                Zip: {data.onSiteContact.zip}
              </p>
              <p className="text-gray-900 text-sm">
                Phone number: {data.onSiteContact.phoneNumber}
              </p>
            </div>
          </div>

          <div className="w-2/4 border-r border-b border-l border-gray-400 lg:border-l-0 lg:border-t lg:border-gray-400 bg-white rounded-b lg:rounded-b-none lg:rounded-r p-4 flex flex-col justify-between leading-normal">
            <div className="mb-8">
              <div className="text-gray-900 font-bold text-xl mb-2">
                Details
              </div>

              <p className="text-gray-900 text-sm">
                Service type: {data.details.serviceType}
              </p>
              <p className="text-gray-900 text-sm">
                Instructions: {data.details.instructions}
              </p>
              <p className="text-gray-900 text-sm">
                Information: {data.details.information}
              </p>
              <p className="text-gray-900 text-sm">
                Special Materials: {data.details.specialMaterials}
              </p>
              <p className="text-gray-900 text-sm">
                Sercive type: {data.details.serviceType}
              </p>

              {data.vendor === config.VENDORS.CTS && (
                <>
                  <p className="text-gray-900 text-sm">
                    Field engineer: {data.details.fieldEngineer}
                  </p>
                  <p className="text-gray-900 text-sm">
                    Field engineer contact number:{' '}
                    {data.details.fieldEngineerContactNumber}
                  </p>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

Dispatch.propTypes = {
  authToken: PropTypes.string
};

export default privateRoute(Dispatch);
