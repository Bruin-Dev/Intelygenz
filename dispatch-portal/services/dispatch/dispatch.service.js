import React from 'react';
import { API_URLS, axiosInstance } from '../api';
import { dispatchAdapter } from './dispatch.adapter';

export const dispatchService = {
  getAll: async () => {
    const res = await axiosInstance.get(API_URLS.DISPATCH);

    if (res.error) {
      return res.error;
    }

    return res;
  },
  newDispatch: async data => {
    // data adapter
    const res = await axiosInstance.post(API_URLS.DISPATCH, data);

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

    return dispatchAdapter(res.data);
  }
};
