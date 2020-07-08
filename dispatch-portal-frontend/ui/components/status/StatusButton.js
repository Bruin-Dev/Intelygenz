import PropTypes from 'prop-types';
import React, { useEffect, useState } from 'react';

export const TYPES_STATUS = {
  newDispatch: {
    value: 'New Dispatch',
    color: 'bg-teal-500'
  },
  open: {
    value: 'Open',
    color: 'bg-teal-500'
  },
  requestConfirmed: {
    value: 'Request Confirmed',
    color: 'bg-orange-500'
  },
  scheduled: {
    value: 'Scheduled',
    color: 'bg-orange-500'
  },
  techArrived: {
    value: 'Tech Arrived',
    color: 'bg-yellow-500'
  },
  onSite: {
    value: 'On Site',
    color: 'bg-yellow-500'
  },
  repairCompleted: {
    value: 'Repair Completed',
    color: 'bg-green-500'
  },
  completed: {
    value: 'Completed',
    color: 'bg-green-500'
  },
  completePendingCollateral: {
    value: 'Complete Pending Collateral',
    color: 'bg-blue-500'
  },
  cancelled: {
    value: 'Cancelled',
    color: 'bg-red-500'
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
      // CTS status
      case TYPES_STATUS.open.value:
        setButtonClass(TYPES_STATUS.open.color);
        return;
      case TYPES_STATUS.scheduled.value:
        setButtonClass(TYPES_STATUS.scheduled.color);
        return;
      case TYPES_STATUS.onSite.value:
        setButtonClass(TYPES_STATUS.onSite.color);
        return;
      case TYPES_STATUS.completed.value:
        setButtonClass(TYPES_STATUS.completed.color);
        return;
      case TYPES_STATUS.completePendingCollateral.value:
        setButtonClass(TYPES_STATUS.completePendingCollateral.color);
        return;
      case TYPES_STATUS.cancelled.value:
        setButtonClass(TYPES_STATUS.cancelled.color);
        return;
      default:
        setButtonClass(TYPES_STATUS.newDispatch.color);
    }
  }, [status]);

  return (
    <button
      data-testid="statusButton-component"
      type="button"
      className={`${buttonClass} cursor-pointer text-white text-xs font-bold py-2 px-4`}
      style={{ cursor: 'auto' }}
    >
      {status}
    </button>
  );
};

StatusButton.propTypes = {
  status: PropTypes.string
};
