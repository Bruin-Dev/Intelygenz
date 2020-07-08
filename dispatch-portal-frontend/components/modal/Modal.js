import { useState } from 'react';
import PropTypes from 'prop-types';
import './Modal.scss';

function Modal({ textModal, titleModal, buttonText, callbackResult }) {
  const [isOpen, setIsOpen] = useState(false);

  const outFunction = () => {
    setIsOpen(false);
    callbackResult(true);
  };

  return (
    <>
      <button
        data-testid="modal-component-open-button"
        type="button"
        className="modal-open bg-transparent hover:bg-teal-500 text-teal-700 hover:text-white py-2 px-4 border border-teal-500 hover:border-transparent rounded"
        onClick={() => setIsOpen(!isOpen)}
      >
        {buttonText}
      </button>

      <div
        data-testid="modal-component"
        className={
          isOpen
            ? 'modal modal-active fixed w-full h-full top-0 left-0 flex items-center justify-center'
            : 'modal opacity-0 pointer-events-none fixed w-full h-full top-0 left-0 flex items-center justify-center'
        }
      >
        <div className="modal-overlay absolute w-full h-full bg-gray-900 opacity-50">
          {' '}
        </div>

        <div className="modal-container bg-white w-11/12 md:max-w-md mx-auto rounded shadow-lg z-50 overflow-y-auto">
          <button
            type="button"
            className="modal-close absolute top-0 right-0 cursor-pointer flex flex-col items-center mt-4 mr-4 text-white text-sm z-50"
            onClick={() => setIsOpen(false)}
            data-testid="modal-component-general-close"
          >
            <svg
              className="fill-current text-white"
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 18 18"
            >
              <path d="M14.53 4.53l-1.06-1.06L9 7.94 4.53 3.47 3.47 4.53 7.94 9l-4.47 4.47 1.06 1.06L9 10.06l4.47 4.47 1.06-1.06L10.06 9z"></path>
            </svg>
          </button>

          <div className="modal-content py-4 text-left px-6">
            <div className="flex justify-between items-center pb-3">
              <p className="text-2xl font-bold">{titleModal}</p>
              <button
                type="button"
                className="modal-close cursor-pointer z-50"
                onClick={() => setIsOpen(false)}
                data-testid="modal-component-container-close"
              >
                <svg
                  className="fill-current text-black"
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 18 18"
                >
                  <path d="M14.53 4.53l-1.06-1.06L9 7.94 4.53 3.47 3.47 4.53 7.94 9l-4.47 4.47 1.06 1.06L9 10.06l4.47 4.47 1.06-1.06L10.06 9z"></path>
                </svg>
              </button>
            </div>

            <p>{textModal}</p>

            <div className="flex justify-end pt-2">
              <button
                type="button"
                className="px-4 bg-transparent p-3 rounded-lg text-teal-500 hover:bg-gray-100 hover:text-teal-400 mr-2"
                onClick={outFunction}
                data-testid="modal-component-confirm-button"
              >
                Yes
              </button>
              <button
                type="button"
                className="modal-close px-4 bg-teal-500 p-3 rounded-lg text-white hover:bg-teal-400"
                onClick={() => setIsOpen(false)}
                data-testid="modal-component-cancel-button"
              >
                No
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

Modal.propTypes = {
  textModal: PropTypes.string.isRequired,
  titleModal: PropTypes.string.isRequired,
  buttonText: PropTypes.string.isRequired,
  callbackResult: PropTypes.func.isRequired
};

export default Modal;
