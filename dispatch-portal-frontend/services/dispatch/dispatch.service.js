import { API_URLS, axiosInstance } from '../api';
import {
  dispatchLitInAdapter,
  dispatchLitOutAdapter
} from './dispatch.adapter';

export const dispatchService = {
  getAll: async () => {
    const res = await axiosInstance.get(API_URLS.DISPATCH);

    if (res.error) {
      return res.error;
    }

    return res;
  },
  newDispatch: async data => {
    const res = await axiosInstance.post(
      API_URLS.DISPATCH,
      dispatchLitOutAdapter(data)
    );

    console.log(res);

    if (res.error) {
      return res.error;
    }

    return res;
  },
  get: async id => {
    const res = await axiosInstance.get(`${API_URLS.DISPATCH}/${id}`);

    if (res.error) {
      return res.error;
    }

    return dispatchLitInAdapter(res.data);
  },
  uploadFiles: async (id, data) => {
    const res = await axiosInstance.post(API_URLS.UPLOAD_FILES, data);

    if (res.error) {
      return false;
    }

    return true;
  }
};
