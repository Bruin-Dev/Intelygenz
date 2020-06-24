import React from 'react';
import PropTypes from 'prop-types';
import { Routes } from '../../../config/routes';

function VendorDispatchLink({ dispatchId, vendor }) {
  return (
    <span data-testid="vendorDispatchLink-component">
      {vendor}(
      <a href={`${Routes.DISPATCH()}/${dispatchId}?vendor=${vendor}`}>
        {dispatchId}
      </a>
      )
    </span>
  );
}

VendorDispatchLink.propTypes = {
  dispatchId: PropTypes.string,
  vendor: PropTypes.string
};

export default VendorDispatchLink;
