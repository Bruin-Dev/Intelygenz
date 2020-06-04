import React from 'react';
import PropTypes from 'prop-types';
import '../ui/styles/_all.scss';
import '../ui/styles/tailwind.scss';

function MyApp({ Component, pageProps }) {
  return <Component {...pageProps} />;
}

MyApp.propTypes = {
  Component: PropTypes.elementType,
  pageProps: PropTypes.object
};

export default MyApp;
