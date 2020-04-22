import React, { useEffect, useState } from 'react';
import PropTypes from 'prop-types';
import { useRouter } from 'next/router';
import { dispatchService } from '../../services/dispatch/dispatch.service';
import { privateRoute } from '../../components/privateRoute/PrivateRoute';
import Menu from '../../components/menu/Menu';

function Dispatch({ authToken }) {
  const router = useRouter();
  const { id } = router.query;

  const [data, setData] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function getInfoDispatch() {
      const response = await dispatchService.get(id);
      setData(response);
      setIsLoading(false);
    }
    getInfoDispatch();
  }, [id]);

  return (
    <div>
      <Menu authToken={authToken} />
      {isLoading ? (
        <p>Loading...</p>
      ) : (
        <>
          <h3>Info dispatch: {data.id}</h3>
          <p>
            <b>Vendor:</b> {data.vendor}
          </p>
          <p>
            <b>SLA Level:</b> {data.slaLevel}
          </p>
          <p>
            <b>Mettel Id:</b> {data.mettelId}
          </p>
          <p>
            <b>Local time of dispatch:</b> {data.timeDispatch}
          </p>
          <p>
            <b>Time Zone Local:</b> {data.timeZone}
          </p>
          <br />
          <h3>Requester</h3>
          <p>
            <b>Name:</b> {data.requester.name}
          </p>
          <p>
            <b>Email:</b> {data.requester.email}
          </p>
          <p>
            <b>Department:</b> {data.requester.department}
          </p>
          <p>
            <b>Phone number:</b> {data.requester.phoneNumber}
          </p>
          <br />
          <h3>On-Site Contact</h3>
          <p>
            <b>Site:</b> {data.onSiteContact.site}
          </p>
          <p>
            <b>Street:</b> {data.onSiteContact.street}
          </p>
          <p>
            <b>City:</b> {data.onSiteContact.city}
          </p>
          <p>
            <b>State:</b> {data.onSiteContact.state}
          </p>
          <p>
            <b>Zip:</b> {data.onSiteContact.zip}
          </p>
          <p>
            <b>Phone number:</b> {data.onSiteContact.phoneNumber}
          </p>
          <br />
          <h3>Details</h3>
          <p>
            <b>Service type:</b> {data.details.serviceType}
          </p>
          <p>
            <b>Instructions:</b> {data.details.instructions}
          </p>
          <p>
            <b>Information:</b> {data.details.information}
          </p>
          <p>
            <b>Special Materials:</b> {data.details.specialMaterials}
          </p>
          <p>
            <b>Sercive type:</b> {data.details.serviceType}
          </p>
        </>
      )}
    </div>
  );
}

Dispatch.propTypes = {
  authToken: PropTypes.string
};

export default privateRoute(Dispatch);
