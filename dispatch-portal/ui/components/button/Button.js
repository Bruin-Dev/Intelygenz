import React from 'react';
import PropTypes from 'prop-types';

export const ButtonExample = ({ children }) => (
  <button type="button" onClick={() => alert('Clicked button!')}>
    {children}
  </button>
);

ButtonExample.propTypes = {
  children: PropTypes.element
};
