import { API_URLS } from '../api.config';
import axiosInstance from '../api';
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
        data: res.data.list_dispatch.map(dispatch =>
          dispatchLitInAdapter({ ...dispatch, vendor: res.data.vendor })
        )
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
      const res = await axiosInstance.post(API_URLS.UPLOAD_FILES, data);

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
      return { error };
    }
    if (error.request) {
      console.log(error.request);
    } else {
      console.log('Error', error.message);
    }
    console.log(error);
  }
};
