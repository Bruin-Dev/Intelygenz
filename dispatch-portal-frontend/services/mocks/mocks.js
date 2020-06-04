import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { dispatchList } from './list-dispatch.mock';
import { API_URLS, baseConfig } from '../api.config';
import { mockLitSingleDispatch } from './single-dispatch.mock';

const axiosInstanceMocks = axios.create(baseConfig);
const mockadapter = new MockAdapter(axiosInstanceMocks, {
  delayResponse: 1000
});

mockadapter.onPost(API_URLS.LOGIN).reply(200, {
  token: 'XXXX-fake-token'
});

mockadapter.onGet(API_URLS.DISPATCH).reply(200, {
  vendor: 'lit',
  list_dispatch: dispatchList.data
});

mockadapter.onPost(API_URLS.DISPATCH).reply(204, { id: 123 });

mockadapter.onPost(API_URLS.UPLOAD_FILES).reply(204);

mockadapter
  .onGet(new RegExp(`${API_URLS.DISPATCH}/*`))
  .reply(200, mockLitSingleDispatch);

export default axiosInstanceMocks;
