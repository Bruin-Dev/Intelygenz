import PropTypes from 'prop-types';
import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useForm } from 'react-hook-form';
import { privateRoute } from '../components/privateRoute/PrivateRoute';
import Menu from '../components/menu/Menu';
import Loading from '../components/loading/Loading';
import { dispatchService } from '../services/dispatch/dispatch.service';
import { Routes } from '../config/routes';
import './new-dispatch.scss';

function NewDispatch({ authToken }) {
  const router = useRouter();
  const { register, handleSubmit, errors } = useForm();
  const [response, setResponse] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [files, setFiles] = useState([]);

  const deleteFile = async index => {
    const auxArraySlice = [...files]; // For react state
    auxArraySlice.splice(index, 1);
    setFiles(auxArraySlice);
  };

  const onChangeHandlerFiles = async e => {
    e.preventDefault();
    setFiles([...files, ...e.target.files]);
  };

  const uploadFiles = async dispatchId => {
    const data = new FormData();
    files.map((file, index) => data.append('file', files[index]));

    const res = await dispatchService.uploadFiles(dispatchId, data);
    return res;
  };

  const onSubmit = async data => {
    setIsLoading(true);

    const res = await dispatchService.newDispatch(data);
    if (!res.error && res.data && res.data.id) {
      // Upload files
      const resFiles = await uploadFiles(res.data.id);
      if (resFiles) {
        // Go to details
        router.push(`${Routes.DISPATCH()}/${res.data.id}`);
        return;
      }
    }
    // Todo: show/add upload error
    setResponse(res);
    setIsLoading(false);
  };

  return (
    <>
      <Menu authToken={authToken} />
      <div className="new-dispatch-wrapper">
        <p className="form-title">New Dispatch Request</p>
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="brick">
            <label htmlFor="dateDispatch">
              Date of dispatch <br />
              <input
                type="date"
                name="dateDispatch"
                id="dateDispatch"
                ref={register({ required: true })}
                className={errors.dateDispatch && 'error'}
              />
              {errors.dateDispatch && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="timeDispatch">
              Time of dispatch (Local)
              <br />
              <select
                name="timeDispatch"
                id="timeDispatch"
                ref={register({ required: true })}
                className={errors.timeDispatch && 'error'}
              >
                <option value="option1">Option 1</option>
                <option value="option2">Option 2</option>
                <option value="option3">Option 3</option>
                <option value="option4">Option 4</option>
              </select>
              {errors.timeDispatch && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="timeZone">
              Time Zone (Local)
              <br />
              <select
                name="timeZone"
                id="timeZone"
                ref={register({ required: true })}
                className={errors.timeZone && 'error'}
              >
                <option value="option1">Option 1</option>
                <option value="option2">Option 2</option>
                <option value="option3">Option 3</option>
                <option value="option4">Option 4</option>
              </select>
              {errors.timeZone && (
                <p className="error">This field is required</p>
              )}
            </label>
          </div>
          <div className="brick">
            <div className="line">
              <p className="brick-title">Vendor</p>
              <label className="checkbox" htmlFor="vendor">
                CTS
                <input
                  type="radio"
                  name="vendor"
                  value="cts"
                  id="cts"
                  ref={register({ required: true })}
                  className={errors.vendor && 'error'}
                />
                <span className="checkmark" />
              </label>
              <label className="checkbox" htmlFor="lit">
                LIT
                <input
                  type="radio"
                  name="vendor"
                  value="lit"
                  id="lit"
                  ref={register({ required: true })}
                  className={errors.vendor && 'error'}
                />
                <span className="checkmark" />
              </label>
              {errors.vendor && <p className="error">This field is required</p>}
            </div>
            <br />
            <label htmlFor="slaLevel">
              SLA Level
              <br />
              <select
                name="slaLevel"
                id="slaLevel"
                ref={register({ required: true })}
                className={errors.slaLevel && 'error'}
              >
                <option value="option1">Option 1</option>
                <option value="option2">Option 2</option>
                <option value="option3">Option 3</option>
                <option value="option4">Option 4</option>
              </select>
              {errors.slaLevel && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="mettelId">
              MetTel Ticket ID <br />
              <input
                type="text"
                name="mettelId"
                id="mettelId"
                ref={register({ required: true })}
                className={errors.mettelId && 'error'}
              />
              {errors.mettelId && (
                <p className="error">This field is required</p>
              )}
            </label>
          </div>
          <p className="section-title">Location</p>
          <div className="brick">
            <label htmlFor="owner">
              Name / Owner
              <br />
              <input
                type="text"
                name="owner"
                id="owner"
                ref={register({ required: true })}
                className={errors.owner && 'error'}
              />
              {errors.owner && <p className="error">This field is required</p>}
            </label>
            <br />
            <label htmlFor="address1">
              Address Line 1<br />
              <input
                type="text"
                name="address1"
                id="address1"
                ref={register({ required: true })}
                className={errors.address1 && 'error'}
              />
              {errors.address1 && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="address2">
              Address Line 2<br />
              <input
                type="text"
                name="address2"
                id="address2"
                ref={register({ required: true })}
                className={errors.address2 && 'error'}
              />
              {errors.address2 && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="city">
              City
              <br />
              <input
                type="text"
                name="city"
                id="city"
                ref={register({ required: true })}
                className={errors.city && 'error'}
              />
              {errors.city && <p className="error">This field is required</p>}
            </label>
            <br />
            <label className="half" htmlFor="state">
              State
              <br />
              <select
                name="state"
                id="state"
                ref={register({ required: true })}
                className={errors.state && 'error'}
              >
                <option value="option1">Option 1</option>
                <option value="option2">Option 2</option>
                <option value="option3">Option 3</option>
                <option value="option4">Option 4</option>
              </select>
              {errors.state && <p className="error">This field is required</p>}
            </label>
            <label className="half right" htmlFor="zip">
              Zip Code
              <br />
              <input
                type="text"
                name="zip"
                id="zip"
                ref={register({ required: true })}
                className={errors.zip && 'error'}
              />
              {errors.zip && <p className="error">This field is required</p>}
            </label>
          </div>
          <div className="brick">
            <p className="brick-title">On-Site Contact</p>
            <label className="half" htmlFor="firstName">
              First Name
              <br />
              <input
                type="text"
                name="firstName"
                id="firstName"
                ref={register({ required: true })}
                className={errors.firstName && 'error'}
              />
              {errors.firstName && (
                <p className="error">This field is required</p>
              )}
            </label>
            <label className="half right" htmlFor="lastName">
              Last Name
              <br />
              <input
                type="text"
                name="lastName"
                id="lastName"
                ref={register({ required: true })}
                className={errors.lastName && 'error'}
              />
              {errors.lastName && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="phoneNumber">
              Phone Number
              <br />
              <input
                type="number"
                name="phoneNumber"
                id="phoneNumber"
                ref={register({ required: true })}
                className={errors.phoneNumber && 'error'}
              />
              {errors.phoneNumber && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="email">
              Email
              <br />
              <input
                type="email"
                name="email"
                id="email"
                ref={register({ required: true })}
                className={errors.email && 'error'}
              />
              {errors.email && <p className="error">This field is required</p>}
            </label>
          </div>
          <p className="section-title">Details</p>
          <div className="brick">
            <p>Service Type</p>
            {errors.serviceType && (
              <p className="error">This field is required</p>
            )}
            <label className="radio" htmlFor="serviceType">
              Troubleshoot
              <input
                type="radio"
                name="serviceType"
                value="troubleshoot"
                id="serviceType"
                ref={register({ required: true })}
                className={errors.serviceType ? 'radio error' : 'radio'}
              />
              <span className="checkmark" />
            </label>
            <br />
            <label className="radio" htmlFor="serviceType">
              Part Replacement
              <input
                type="radio"
                name="serviceType"
                value="replacement"
                id="serviceType"
                ref={register({ required: true })}
                className={errors.serviceType ? 'radio error' : 'radio'}
              />
              <span className="checkmark" />
            </label>
            <br />
            <label className="radio" htmlFor="serviceType">
              Cable Run
              <input
                type="radio"
                name="serviceType"
                value="cable"
                id="service-type"
                ref={register({ required: true })}
                className={errors.serviceType ? 'radio error' : 'radio'}
              />
              <span className="checkmark" />
            </label>
            <br />
            <label htmlFor="issues">
              Issue(s) Experienced
              <br />
              <textarea
                rows="4"
                cols="50"
                name="issues"
                id="issues"
                ref={register({ required: true })}
                className={errors.issues && 'error'}
              />
              {errors.issues && <p className="error">This field is required</p>}
            </label>
          </div>
          <div className="brick">
            <label htmlFor="materials">
              Materials Needed
              <br />
              <textarea
                rows="4"
                cols="50"
                name="materials"
                id="materials"
                ref={register({ required: true })}
                className={errors.materials && 'error'}
              />
              {errors.materials && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="instructions">
              Arrival Instructions
              <br />
              <textarea
                rows="4"
                cols="50"
                name="instructions"
                id="instructions"
                ref={register({ required: true })}
                className={errors.instructions && 'error'}
              />
              {errors.instructions && (
                <p className="error">This field is required</p>
              )}
            </label>
          </div>
          <p className="section-title">Attachments</p>
          <div className="brick">
            <div className="file">
              <label htmlFor="files" className="btn">
                Add File/s
                <input
                  id="files"
                  style={{ visibility: 'hidden' }}
                  type="file"
                  multiple
                  onChange={onChangeHandlerFiles}
                />
              </label>
              {files.length ? (
                <div>
                  <ol>
                    {files.map((file, index) => (
                      <li key={`file-name-${index}`}>
                        {file.name}{' '}
                        <button type="button" onClick={() => deleteFile(index)}>
                          Delete file
                        </button>
                      </li>
                    ))}
                  </ol>
                </div>
              ) : (
                <p>No Files Chosen</p>
              )}
            </div>
          </div>
          <p className="section-title">Requester</p>
          <div className="brick">
            <label className="half" htmlFor="firstNameRequester">
              First Name
              <br />
              <input
                type="text"
                name="firstNameRequester"
                id="firstNameRequester"
                ref={register({ required: true })}
                className={errors.firstNameRequester && 'error'}
              />
              {errors.firstNameRequester && (
                <p className="error">This field is required</p>
              )}
            </label>
            <label className="half right" htmlFor="lastNameRequester">
              Last Name
              <br />
              <input
                type="text"
                name="lastNameRequester"
                id="lastNameRequester"
                ref={register({ required: true })}
                className={errors.lastNameRequester && 'error'}
              />
              {errors.lastNameRequester && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="department">
              MelTel Department
              <br />
              <select
                name="department"
                id="department"
                ref={register({ required: true })}
                className={errors.department && 'error'}
              >
                <option value="option1">Option 1</option>
                <option value="option2">Option 2</option>
                <option value="option3">Option 3</option>
                <option value="option4">Option 4</option>
              </select>
              {errors.department && (
                <p className="error">This field is required</p>
              )}
            </label>
          </div>
          <div className="brick">
            <label htmlFor="phoneNumberRequester">
              Pnone Number
              <br />
              <input
                type="number"
                name="phoneNumberRequester"
                id="phoneNumberRequester"
                ref={register({ required: true })}
                className={errors.phoneNumberRequester && 'error'}
              />
              {errors.phoneNumberRequester && (
                <p className="error">This field is required</p>
              )}
            </label>
            <br />
            <label htmlFor="emailRequester">
              Email
              <br />
              <input
                type="email"
                name="emailRequester"
                id="emailRequester"
                ref={register({ required: true })}
                className={errors.emailRequester && 'error'}
              />
              {errors.emailRequester && (
                <p className="error">This field is required</p>
              )}
            </label>
          </div>
          {isLoading ? (
            <Loading />
          ) : (
            <button className="login" type="submit">
              Submit
            </button>
          )}
          {response.error && (
            <p className="error">Error, please try again later</p>
          )}
        </form>
      </div>
    </>
  );
}

NewDispatch.propTypes = {
  authToken: PropTypes.string
};

export default privateRoute(NewDispatch);
