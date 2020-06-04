import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

export const TYPES_STATUS = {
  newDispatch: {
    value: 'New Dispatch',
    color: 'bg-teal-500 hover:bg-teal-700'
  },
  requestConfirmed: {
    value: 'Request Confirmed',
    color: 'bg-orange-500 hover:bg-orange-700'
  },
  techArrived: {
    value: 'Tech Arrived',
    color: 'bg-yellow-500 hover:bg-yellow-700'
  },
  repairCompleted: {
    value: 'Repair Completed',
    color: 'bg-green-500 hover:bg-green-700'
  }
};

export const StatusButton = ({ status }) => {
  const [buttonClass, setButtonClass] = useState();

  useEffect(() => {
    switch (status) {
      case TYPES_STATUS.newDispatch.value:
        setButtonClass(TYPES_STATUS.newDispatch.color);
        return;
      case TYPES_STATUS.requestConfirmed.value:
        setButtonClass(TYPES_STATUS.requestConfirmed.color);
        return;
      case TYPES_STATUS.techArrived.value:
        setButtonClass(TYPES_STATUS.techArrived.color);
        return;
      case TYPES_STATUS.repairCompleted.value:
        setButtonClass(TYPES_STATUS.repairCompleted.color);
        return;
      default:
        setButtonClass(TYPES_STATUS.newDispatch.color);
    }
  }, [status]);

  return (
    <button
      data-testid="statusButton-component"
      type="button"
      className={`${buttonClass} cursor-not-allowed text-white text-xs font-bold py-2 px-4`}
    >
      {status}
    </button>
  );
};

StatusButton.propTypes = {
  status: PropTypes.string
};
