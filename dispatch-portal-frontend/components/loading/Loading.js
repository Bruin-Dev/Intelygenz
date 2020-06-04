import React from 'react';
import './Loading.scss';

function Loading() {
  return (
    <div className="wrapper-loader" data-testid="loading-component">
      <div className="loader" />
    </div>
  );
}

export default Loading;
