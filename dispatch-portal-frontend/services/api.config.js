import { config } from '../config/config';

export const API_URLS = {
  LOGIN: '/login',
  DISPATCH_LIT: '/lit/dispatch',
  DISPATCH_CTS: '/cts/dispatch',
  UPLOAD_FILES: '/upload'
};

export const baseConfig = {
  baseURL: config.baseApi,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
};
