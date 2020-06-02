import PropTypes from 'prop-types';
import { useEffect, useState } from 'react';

const TYPES_STATUS = {
  newDispatch: 'New Dispatch',
  requestConfirmed: 'Request Confirmed',
  techArrived: 'Tech Arrived',
  repairCompleted: 'Repair Completed'
};

export const StatusButton = ({ status }) => {
  const [buttonClass, setButtonClass] = useState();

  useEffect(() => {
    switch (status) {
      case TYPES_STATUS.newDispatch:
        setButtonClass('bg-teal-500 hover:bg-teal-700');
        return;
      case TYPES_STATUS.requestConfirmed:
        setButtonClass('bg-orange-500 hover:bg-orange-700');
        return;
      case TYPES_STATUS.techArrived:
        setButtonClass('bg-yellow-500 hover:bg-yellow-700');
        return;
      case TYPES_STATUS.repairCompleted:
        setButtonClass('bg-green-500 hover:bg-green-700');
        return;
      default:
        setButtonClass('bg-blue-500 hover:bg-blue-700');
    }
  }, [status]);

  return (
    <button
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
