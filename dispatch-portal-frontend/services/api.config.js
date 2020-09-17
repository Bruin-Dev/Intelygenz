import { config } from '../config/config';

export const API_URLS = {
  LOGIN: '/login',
  DISPATCH_LIT: '/lit/dispatch',
  DISPATCH_CTS: '/cts/dispatch',
  UPLOAD_FILES: '/upload',
  GET_LOCATION_BY_TICKET_ID: '/bruin/ticket_address'
};

export const baseConfig = {
  baseURL: config.baseApi,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
};
