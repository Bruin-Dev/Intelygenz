import axios from 'axios';
import { config } from '../config/config';
import { baseConfig } from './api.config';
import axiosInstanceMocks from './mocks/mocks';

const axiosInstance = axios.create(baseConfig);

export default config.mocks ? axiosInstanceMocks : axiosInstance;
