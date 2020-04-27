import axios from 'axios';
import { config } from '../config/config';

export const API_URLS = {
  LOGIN: '/login',
  DISPATCH: '/lit/dispatch',
  UPLOAD_FILES: '/upload'
};

export const baseConfig = {
  baseURL: config.baseApi,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json;charset=utf-8'
  }
};

export const axiosInstance = axios.create(baseConfig);
