import { API_URLS, axiosInstance } from '../api';
import { axiosInstanceMocks } from '../mocks/mocks';
import {
  dispatchLitInAdapter,
  dispatchLitOutAdapter
} from './dispatch.adapter';

export const dispatchService = {
  getAll: async () => {
    try {
      const res = await axiosInstance.get(API_URLS.DISPATCH);

      if (res.error) {
        return { error: res.error };
      }

      return {
        data: res.data.list_dispatch.map(dispatch => ({
          ...dispatch,
          vendor: res.data.vendor
        }))
      };
    } catch (error) {
      return dispatchService.captureErrorGeneric(error);
    }
  },
  newDispatch: async data => {
    try {
      const res = await axiosInstance.post(
        API_URLS.DISPATCH,
        dispatchLitOutAdapter(data)
      );

      if (res.error) {
        return res.error;
      }

      return res;
    } catch (error) {
      return dispatchService.captureErrorGeneric(error);
    }
  },
  get: async id => {
    try {
      const res = await axiosInstance.get(`${API_URLS.DISPATCH}/${id}`);

      if (res.error) {
        return res.error;
      }
      return dispatchLitInAdapter(res.data);
    } catch (error) {
      return dispatchService.captureErrorGeneric(error);
    }
  },
  uploadFiles: async (id, data) => {
    try {
      const res = await axiosInstanceMocks.post(API_URLS.UPLOAD_FILES, data);

      if (res.error) {
        return false;
      }

      return true;
    } catch (error) {
      return dispatchService.captureErrorGeneric(error);
    }
  },
  captureErrorGeneric: error => {
    if (error.response) {
      /*
       * The request was made and the server responded with a
       * status code that falls out of the range of 2xx
       */
      console.log(error.response.data);
      console.log(error.response.status);
      console.log(error.response.headers);
      return { error };
    }
    if (error.request) {
      /*
       * The request was made but no response was received, `error.request`
       * is an instance of XMLHttpRequest in the browser and an instance
       * of http.ClientRequest in Node.js
       */
      console.log(error.request);
    } else {
      // Something happened in setting up the request and triggered an Error
      console.log('Error', error.message);
    }
    console.log(error);
  }
};
