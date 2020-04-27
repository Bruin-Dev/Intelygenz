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
        <>
          <div className="wrapper-dispatch">
            <div className="flex mb-4">
              <div className="w-1/2 h-12">
                <h3>Info dispatch: {data.id}</h3>
                <ul>
                  <li>
                    <b>Vendor:</b> {data.vendor}
                  </li>
                  <li>
                    <b>SLA Level:</b> {data.slaLevel}
                  </li>
                  <li>
                    <b>Status:</b>{' '}
                    <button type="button" className={data.status}>
                      {data.status}
                    </button>
                  </li>
                  <li>
                    <b>Mettel Id:</b> {data.mettelId}
                  </li>
                  <li>
                    <b>Local time of dispatch:</b> {data.timeDispatch}
                  </li>
                  <li>
                    <b>Time Zone Local:</b> {data.timeZone}
                  </li>
                </ul>
              </div>
              <div className="w-1/2 h-12">
                <h3>Requester</h3>
                <ul>
                  <li>
                    <b>Name:</b> {data.requester.name}
                  </li>
                  <li>
                    <b>Email:</b> {data.requester.email}
                  </li>
                  <li>
                    <b>Department:</b> {data.requester.department}
                  </li>
                  <li>
                    <b>Phone number:</b> {data.requester.phoneNumber}
                  </li>
                </ul>
              </div>
            </div>
            <div className="flex mb-4">
              <div className="w-1/2 h-12">
                <h3>On-Site Contact</h3>
                <ul>
                  <li>
                    <b>Site:</b> {data.onSiteContact.site}
                  </li>
                  <li>
                    <b>Street:</b> {data.onSiteContact.street}
                  </li>
                  <li>
                    <b>City:</b> {data.onSiteContact.city}
                  </li>
                  <li>
                    <b>State:</b> {data.onSiteContact.state}
                  </li>
                  <li>
                    <b>Zip:</b> {data.onSiteContact.zip}
                  </li>
                  <li>
                    <b>Phone number:</b> {data.onSiteContact.phoneNumber}
                  </li>
                </ul>
              </div>
              <div className="w-1/2 h-12">
                <h3>Details</h3>
                <ul>
                  <li>
                    <b>Service type:</b> {data.details.serviceType}
                  </li>
                  <li>
                    <b>Instructions:</b> {data.details.instructions}
                  </li>
                  <li>
                    <b>Information:</b> {data.details.information}
                  </li>
                  <li>
                    <b>Special Materials:</b> {data.details.specialMaterials}
                  </li>
                  <li>
                    <b>Sercive type:</b> {data.details.serviceType}
                  </li>

                  {data.vendor === config.VENDORS.CTS && (
                    <>
                      <li>
                        <b>Field engineer:</b> {data.details.fieldEngineer}
                      </li>
                      <li>
                        <b>Field engineer contact number:</b>{' '}
                        {data.details.fieldEngineerContactNumber}
                      </li>
                    </>
                  )}
                </ul>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

Dispatch.propTypes = {
  authToken: PropTypes.string
};

export default privateRoute(Dispatch);
