import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { dispatchLitList } from './data/lit/list-dispatch.mock';
import { API_URLS, baseConfig } from '../api.config';
import { mockLitSingleDispatch } from './data/lit/single-dispatch.mock';
import { dispatchCtsList } from './data/cts/list-dispatch.mock';
import { mockCtsSingleDispatch } from './data/cts/single-dispatch.mock';
import { getLocationByTicketIdMock } from './data/location/location.mock';

const axiosInstanceMocks = axios.create(baseConfig);
const mockadapter = new MockAdapter(axiosInstanceMocks, {
  delayResponse: 1000
});

/** ****
 *
 * GENERAL MOCKS
 *
 *
 */
mockadapter.onPost(API_URLS.LOGIN).reply(200, {
  token: 'XXXX-fake-token'
});

mockadapter.onPost(API_URLS.UPLOAD_FILES).reply(204);
/** ****
 *
 * LIT MOCKS
 *
 *
 */
mockadapter.onGet(API_URLS.DISPATCH_LIT).reply(200, {
  vendor: 'lit',
  list_dispatch: dispatchLitList.data
});

mockadapter.onPost(API_URLS.DISPATCH_LIT).reply(204, { id: 123 });

mockadapter
  .onGet(new RegExp(`${API_URLS.DISPATCH_LIT}/*`))
  .reply(200, mockLitSingleDispatch);

mockadapter.onPatch(new RegExp(`${API_URLS.DISPATCH_LIT}/*`)).reply(204, {
  ...mockLitSingleDispatch,
  dispatch: { ...mockLitSingleDispatch.dispatch, dispatch_status: 'Cancelled' }
});

/** ****
 *
 * CTS MOCKS
 *
 *
 */
mockadapter.onGet(API_URLS.DISPATCH_CTS).reply(200, {
  vendor: 'cts',
  list_dispatch: dispatchCtsList.data
});

mockadapter.onPost(API_URLS.DISPATCH_CTS).reply(404);

mockadapter
  .onGet(new RegExp(`${API_URLS.DISPATCH_CTS}/*`))
  .reply(200, mockCtsSingleDispatch);

mockadapter.onPatch(new RegExp(`${API_URLS.DISPATCH_CTS}/*`)).reply(204, {
  ...mockCtsSingleDispatch,
  dispatch: {
    ...mockCtsSingleDispatch.dispatch,
    status__c: 'Cancelled'
  }
});

mockadapter
  .onGet(new RegExp(`${API_URLS.GET_LOCATION_BY_TICKET_ID}/*`))
  .reply(200, getLocationByTicketIdMock);
export default axiosInstanceMocks;
